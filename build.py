"""Build the Windows x64 release from the supplied source bundle."""
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
def run(*args): subprocess.run([sys.executable, *args], cwd=root, check=True)
run('-m', 'unittest', '-v')
run('-m','PyInstaller','--noconfirm','--onefile','--name','esp-runner',
    '--collect-all','esptool','--copy-metadata','esptool','--distpath','tools','esp_runner.py')
run('-m','PyInstaller','--noconfirm','--onefile','--windowed','--name','ChromaPlayer-Installer',
    '--hidden-import','serial.tools.list_ports','--add-data','firmware;firmware',
    '--add-data','tools;tools','--add-data','licenses;licenses',
    '--add-data','LICENSE;.', '--add-data','THIRD_PARTY.md;.', 'app.py')
