import hashlib,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import build_installer

class SourceBuildTests(unittest.TestCase):
 def fixture(self,base):
  bundle=base/'payload';bundle.mkdir();entries=[]
  for n in range(4):
   entries.append({'game_relative_path':f'LocalData/Patch/{n}/table','payload_relative_path':f'{n}/table','sha256_original':'0'*64,'sha256_patched':hashlib.sha256(f'valid-{n}'.encode()).hexdigest()})
  corpus=base/'localization/corpus_parallel.jsonl';corpus.parent.mkdir();corpus.write_bytes(b'reviewed corpus')
  m={'translation_version':'1.0.0','files':entries,'corpus_sha256':hashlib.sha256(corpus.read_bytes()).hexdigest()};(bundle/'manifest.json').write_text(json.dumps(m));return m

 def run_prepare(self,base,archive):
  with patch.object(build_installer,'__file__',str(base/'tools/build_installer.py')),patch.object(sys,'argv',['build_installer','--prepare-only','--payload-zip',str(archive)]):
   return build_installer.main()

 def test_bad_hash_rejects_whole_archive_before_first_write(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);m=self.fixture(base);archive=base/'payload.zip'
   with zipfile.ZipFile(archive,'w') as z:
    z.writestr('payload/manifest.json',json.dumps(m))
    for n,e in enumerate(m['files']):z.writestr('payload/'+e['payload_relative_path'],b'tampered' if n==3 else f'valid-{n}'.encode())
   with self.assertRaisesRegex(ValueError,'hash mismatch'):self.run_prepare(base,archive)
   self.assertEqual([p.relative_to(base/'payload').as_posix() for p in (base/'payload').rglob('*')],['manifest.json'])

 def test_other_source_manifest_rejected_without_writing(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);m=self.fixture(base);m['translation_version']='different';archive=base/'payload.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr('payload/manifest.json',json.dumps(m))
   with self.assertRaisesRegex(ValueError,'match source manifest'):self.run_prepare(base,archive)
   self.assertEqual(len(list((base/'payload').rglob('*'))),1)

 def test_changed_corpus_rejected_before_download_or_payload_write(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);self.fixture(base)
   (base/'localization/corpus_parallel.jsonl').write_bytes(b'new translation')
   with patch.object(build_installer,'__file__',str(base/'tools/build_installer.py')),patch.object(sys,'argv',['build_installer','--prepare-only']),patch.object(build_installer.subprocess,'run') as run,patch.object(build_installer.urllib.request,'urlretrieve') as fetch:
    with self.assertRaisesRegex(ValueError,'current corpus'):build_installer.main()
    run.assert_not_called();fetch.assert_not_called()
   self.assertEqual(len(list((base/'payload').rglob('*'))),1)

if __name__=='__main__':unittest.main()
