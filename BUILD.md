# Compilare l'installer dai sorgenti

Windows con Python 3.11. Dalla radice del repository:

```powershell
python -m pip install -r requirements-build.txt
python tools/build_installer.py
```

Se il payload non è già presente, il comando scarica `Lost-Light-Italian-Setup-1.0.0.exe` dalla release corrispondente al manifest. Con GitHub CLI disponibile usa `gh`; altrimenti usa l'URL pubblico. Una bozza richiede accesso tramite `gh`, oppure un installer locale:

```powershell
python tools/build_installer.py --payload-exe C:\percorso\Lost-Light-Italian-Setup-1.0.0.exe
```

Non servono i percorsi D: o E: del progetto originale per compilare l'installer. Il comando controlla che manifest della release e manifest dei sorgenti coincidano, verifica tutti gli hash prima di estrarre, estrae il payload dall’EXE senza eseguirlo e avvia PyInstaller. Anche la spec verifica il payload e include soltanto i file dichiarati, oltre a icone e metadati. L'eseguibile viene scritto in `dist/Lost-Light-Italian-Translation.exe`.

`--prepare-only` prepara/verifica il payload senza compilare; `--dist-dir` cambia la cartella di output. Per una nuova versione usare sempre sorgenti e payload della stessa revisione: un manifest diverso viene rifiutato.

La rigenerazione delle traduzioni è un'operazione separata dalla compilazione dell'installer: richiede gli originali verificati della build del gioco, corpus, proposte revisionate e strumenti del progetto. Gli originali del gioco e i backup personali non sono inclusi nel repository.
