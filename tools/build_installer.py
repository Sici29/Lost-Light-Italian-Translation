"""Prepare a checksum-verified release payload and build the Windows GUI EXE."""
from pathlib import Path
import argparse,json,hashlib,zipfile,subprocess,sys,tempfile,shutil,urllib.request,os
from lostlight_it_installer import load_payload_files,safe_path,InstallError

def require(condition,message):
 if not condition:raise ValueError(message)

def verify_corpus_binding(repo,manifest):
 corpus=Path(repo)/'localization/corpus_parallel.jsonl'
 require(corpus.is_file(),'Source corpus is missing')
 require(hashlib.sha256(corpus.read_bytes()).hexdigest()==manifest.get('corpus_sha256'),
         'Payload tables do not match the current corpus; rebuild and stage the tables before compiling')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--payload-zip',type=Path,help='Local release payload ZIP; otherwise download matching version when needed')
 parser.add_argument('--payload-exe',type=Path,help='Extract verified payload from a local installer without running it')
 parser.add_argument('--prepare-only',action='store_true')
 parser.add_argument('--dist-dir',type=Path)
 args=parser.parse_args();repo=Path(__file__).resolve().parents[1];bundle=repo/'payload'
 manifest=json.loads((bundle/'manifest.json').read_text(encoding='utf-8'))
 verify_corpus_binding(repo,manifest)
 try:load_payload_files(bundle);ready=True
 except (InstallError,OSError):ready=False
 if args.payload_zip or args.payload_exe or not ready:
  with tempfile.TemporaryDirectory(prefix='lostlight-build-') as temp:
   archive=args.payload_zip or args.payload_exe
   if archive is None:
    version=manifest['translation_version'];name=f'Lost-Light-Italian-Setup-{version}.exe';archive=Path(temp)/name
    if shutil.which('gh'):
     subprocess.run(['gh','release','download',version,'--repo','Sici29/Lost-Light-Italian-Translation','--pattern',name,'--dir',temp],check=True)
    else:
     urllib.request.urlretrieve(f'https://github.com/Sici29/Lost-Light-Italian-Translation/releases/download/{version}/{name}',archive)
   if archive.suffix.lower()=='.exe':
    from PyInstaller.archive.readers import CArchiveReader
    z=CArchiveReader(str(archive));names={n.replace('\\','/'):n for n in z.toc}
    read=lambda name:z.extract(names[name])
   else:
    z=zipfile.ZipFile(archive);names=z.namelist();require(len(names)==len(set(names)),'Duplicate archive entries')
    read=z.read
   try:
    archived=json.loads(read('payload/manifest.json'));require(archived==manifest,'Release payload does not match source manifest')
    pending=[]
    for e in manifest['files']:
     rel=Path(e['payload_relative_path']);require(not rel.is_absolute() and '..' not in rel.parts,'Invalid payload path')
     target=bundle/rel;safe_path(target)
     require(target.resolve().is_relative_to(bundle.resolve()),'Payload path outside bundle')
     data=read('payload/'+rel.as_posix());require(hashlib.sha256(data).hexdigest()==e['sha256_patched'],'Payload hash mismatch')
     pending.append((target,data))
    for target,data in pending:
     target.parent.mkdir(parents=True,exist_ok=True);tempfile_path=target.with_suffix(target.suffix+'.build-staging');tempfile_path.write_bytes(data);os.replace(tempfile_path,target)
   finally:
    if isinstance(z,zipfile.ZipFile):z.close()
 load_payload_files(bundle)
 print(f'Payload verified: {len(manifest["files"])} files')
 if not args.prepare_only:
  command=[sys.executable,'-m','PyInstaller','--noconfirm']
  if args.dist_dir:command+=['--distpath',str(args.dist_dir.resolve())]
  subprocess.run(command+[str(repo/'Lost-Light-Italian-Translation.spec')],cwd=repo,check=True)
 return 0

if __name__=='__main__':raise SystemExit(main())
