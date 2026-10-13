import tempfile,json,hashlib,unittest
from pathlib import Path
import lostlight_it_installer as app
from unittest.mock import patch
import os,subprocess

class InstallerTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Windows process enumeration')
    @patch.object(app.subprocess, 'check_output', return_value=b'"Game_x64r.exe","57356","Console","1","42 K"\r\n')
    def test_process_check_does_not_open_console(self, query):
        self.assertTrue(app.game_running())
        self.assertEqual(query.call_args.kwargs['creationflags'],subprocess.CREATE_NO_WINDOW)
        self.assertEqual(query.call_args.kwargs['timeout'],10)

    @unittest.skipUnless(os.name == 'nt', 'Windows process enumeration')
    def test_failed_process_check_does_not_assume_game_closed(self):
        for error in [OSError('query unavailable'),subprocess.TimeoutExpired('tasklist',10),subprocess.CalledProcessError(1,'tasklist')]:
            with self.subTest(error=type(error).__name__),patch.object(app.subprocess,'check_output',side_effect=error):
                with self.assertRaises(app.InstallError):
                    app.require_closed()

    @patch.object(app, 'game_running', return_value=False)
    def test_downloader_originals_preserved_over_older_translation_backups(self, _game_running):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);root=base/'game';bundle=base/'payload';state_dir=base/'state';bundle.mkdir();entries=[]
            for n in range(4):
                rel=f'LocalData/Patch/{n}/table';old=f'older-translation-{n}'.encode();official=f'official-{n}'.encode();translated=f'new-translation-{n}'.encode()
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
                src=bundle/str(n);src.write_bytes(translated)
                entries.append({'game_relative_path':rel,'payload_relative_path':str(n),'sha256_original':hashlib.sha256(official).hexdigest(),'sha256_patched':hashlib.sha256(translated).hexdigest(),'sha256_compatible':[hashlib.sha256(old).hexdigest()]})
            (bundle/'manifest.json').write_text(json.dumps({'files':entries,'package_version':'570'}))
            app.install(root,bundle,state_dir)
            state_path=app.state_file(root,state_dir);saved=app.read_state(state_path)
            backup_dir=state_path.parent/state_path.stem/saved['transaction_id']
            for n,e in enumerate(entries):(root/e['game_relative_path']).write_bytes(f'official-{n}'.encode())
            (root/entries[0]['game_relative_path']).write_bytes(b'unknown update')
            with self.assertRaises(app.InstallError):app.restore(root,state_dir,bundle)
            self.assertTrue(state_path.exists())
            (root/entries[0]['game_relative_path']).write_bytes(b'official-0')
            app.restore(root,state_dir,bundle)
            for n,e in enumerate(entries):self.assertEqual((root/e['game_relative_path']).read_bytes(),f'official-{n}'.encode())
            self.assertTrue((backup_dir/'restored_state.json').is_file())
            self.assertEqual(len(list(backup_dir.glob('before_*.bin'))),4)

    @patch.object(app, 'game_running', return_value=False)
    def test_distinct_copies_restore_and_tamper(self, _game_running):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); root=base/'game'; bundle=base/'payload'; state=base/'state'
            bundle.mkdir(); entries=[]
            for n,rel in enumerate(['31/a','42/b','lazy_code/Encrypt_Python/31/a','lazy_code/Encrypt_Python/42/b']):
                original=f'original-{n}'.encode(); patched=f'italiano-{n}'.encode()
                target=root/'LocalData/Patch'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
                src=bundle/rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(patched)
                entries.append({'game_relative_path':f'LocalData/Patch/{rel}','payload_relative_path':rel,'sha256_original':hashlib.sha256(original).hexdigest(),'sha256_patched':hashlib.sha256(patched).hexdigest()})
            # Layout copies share a basename but have distinct destinations/backups.
            for n,rel in enumerate(['Package/UIScript/test.csb','LocalData/Patch/UIScript/test.csb'],start=4):
                original=f'original-{n}'.encode();patched=f'italiano-{n}'.encode()
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
                payload_rel='layouts/'+rel;src=bundle/payload_rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(patched)
                entries.append({'game_relative_path':rel,'payload_relative_path':payload_rel,'sha256_original':hashlib.sha256(original).hexdigest(),'sha256_patched':hashlib.sha256(patched).hexdigest(),'kind':'cocos_layout'})
            rel='Package/UIScript/test_atlas.plist';n=6
            original=f'original-{n}'.encode();patched=f'italiano-{n}'.encode()
            target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
            payload_rel='atlases/'+rel;src=bundle/payload_rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(patched)
            entries.append({'game_relative_path':rel,'payload_relative_path':payload_rel,'sha256_original':hashlib.sha256(original).hexdigest(),'sha256_patched':hashlib.sha256(patched).hexdigest(),'kind':'cocos_atlas'})
            rel='Package/6c/6cffd584-a9dc-4607-b2be-3436c66404f9.6';n=7
            original=f'original-{n}'.encode();patched=f'italiano-{n}'.encode()
            target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
            payload_rel='textures/'+rel;src=bundle/payload_rel;src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(patched)
            entries.append({'game_relative_path':rel,'payload_relative_path':payload_rel,'sha256_original':hashlib.sha256(original).hexdigest(),'sha256_patched':hashlib.sha256(patched).hexdigest(),'kind':'cocos_texture'})
            (bundle/'manifest.json').write_text(json.dumps({'files':entries,'package_version':'570'}))
            app.install(root,bundle,state)
            self.assertTrue(app.installation_intact(root,app.read_state(app.state_file(root,state))))
            for n,e in enumerate(entries):self.assertEqual((root/e['game_relative_path']).read_bytes(),f'italiano-{n}'.encode())
            target=root/entries[0]['game_relative_path']; target.write_bytes(b'game update')
            self.assertFalse(app.installation_intact(root,app.read_state(app.state_file(root,state))))
            with self.assertRaises(app.InstallError):app.restore(root,state)
            target.write_bytes(b'italiano-0');app.restore(root,state)
            for n,e in enumerate(entries):self.assertEqual((root/e['game_relative_path']).read_bytes(),f'original-{n}'.encode())
            target.write_bytes(b'unknown version')
            with self.assertRaises(app.InstallError):app.install(root,bundle,state)
            self.assertEqual((root/entries[1]['game_relative_path']).read_bytes(),b'original-1')
            for invalid in ['Package/aa/6cffd584-a9dc-4607-b2be-3436c66404f9.6',
                            'Engine/6c/6cffd584-a9dc-4607-b2be-3436c66404f9.6',
                            'LocalData/Patch/UIScript/6cffd584-a9dc-4607-b2be-3436c66404f9.6']:
                entries[-1]['game_relative_path']=invalid
                (bundle/'manifest.json').write_text(json.dumps({'files':entries,'package_version':'570'}))
                with self.assertRaises(app.InstallError):app.load_payload_files(bundle)

class FileStatusTests(unittest.TestCase):
    def test_distinguishes_updater_restore_unknown_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def sha(b):return hashlib.sha256(b).hexdigest().upper()
            state={'files':{}}
            for name,content in [('patched',b'italiano'),('restored',b'originale'),('changed',b'new build'),('missing',None)]:
                state['files'][name]={'relative_path':name,'patch_sha256':sha(b'italiano'),'original_sha256':sha(b'originale')}
                if content is not None:(root/name).write_bytes(content)
            self.assertEqual(app.installation_file_counts(root,state),{'patched':1,'original':1,'changed':1,'missing':1})
            self.assertFalse((root/'missing').exists())
            self.assertEqual((root/'restored').read_bytes(),b'originale')

if __name__=='__main__':unittest.main()
