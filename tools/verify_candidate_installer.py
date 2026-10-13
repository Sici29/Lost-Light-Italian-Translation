"""Read executable resources and every embedded payload file; never run it."""
import argparse,hashlib,json,struct
from pathlib import Path
import pefile
from PyInstaller.archive.readers import CArchiveReader

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path,required=True)
    ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--proof',type=Path,required=True)
    a=ap.parse_args();archive=CArchiveReader(str(a.exe))
    names={n.replace('\\','/'):n for n in archive.toc}
    manifest=json.loads(archive.extract(names['payload/manifest.json']))
    source=json.loads((a.repo/'payload/manifest.json').read_text(encoding='utf-8'))
    assert manifest==source,'Embedded manifest differs from current source'
    corpus_hash=hashlib.sha256((a.repo/'localization/corpus_parallel.jsonl').read_bytes()).hexdigest()
    assert manifest['corpus_sha256']==corpus_hash,'Embedded tables belong to another corpus'
    for e in manifest['files']:
        raw=archive.extract(names['payload/'+e['payload_relative_path'].replace('\\','/')])
        assert hashlib.sha256(raw).hexdigest()==e['sha256_patched'],e['game_relative_path']
    pe=pefile.PE(str(a.exe));assert pe.OPTIONAL_HEADER.Subsystem==2,'Console executable'
    icons=[];groups=[]
    for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if kind.id==14:groups.extend(kind.directory.entries)
        if kind.id==3:
            for entry in kind.directory.entries:
                for language in entry.directory.entries:
                    data=language.data.struct;icons.append(pe.get_data(data.OffsetToData,data.Size))
    ico=(a.repo/'assets/lostlight-italiano.ico').read_bytes();count=struct.unpack_from('<H',ico,4)[0]
    source_icons=[]
    for i in range(count):
        size,offset=struct.unpack_from('<II',ico,6+i*16+8);source_icons.append(ico[offset:offset+size])
    assert groups and source_icons and all(image in icons for image in source_icons),'Provided icon images missing from PE'
    proof={'candidate_path':str(a.exe.resolve()),'candidate_sha256':hashlib.sha256(a.exe.read_bytes()).hexdigest(),
           'candidate_size':a.exe.stat().st_size,'embedded_payload_files':len(manifest['files']),
           'texture_files':manifest['texture_files'],'corpus_sha256':corpus_hash,
           'every_embedded_payload_hash_verified':True,'embedded_manifest_matches_current_source':True,
           'gui_pe_subsystem':2,'all_provided_icon_images_embedded':True,'icon_images':count,
           'runtime_verified':False,'gui_visual_smoke_verified':False,'published':False,'game_files_modified':False}
    a.proof.write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))

if __name__=='__main__':main()
