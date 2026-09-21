"""Build on the target OS: python build.py. Firmware is deliberately excluded."""
from pathlib import Path
import subprocess
import sys
import shutil
import zipfile

root=Path(__file__).resolve().parent
subprocess.run([sys.executable,'-m','unittest','-v'],cwd=root,check=True)
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--onedir',
    '--name','PlayOS-Installer','--collect-all','esptool','--copy-metadata','esptool',
    '--hidden-import','serial.tools.list_ports','app.py'],cwd=root,check=True)
package=root/'dist'/'PlayOS-Installer'
for name in ('README.md','LICENSE','THIRD_PARTY.md','requirements.txt'):
    shutil.copy2(root/name,package/name)
sources=package/'third-party-source'; sources.mkdir(exist_ok=True)
subprocess.run([sys.executable,'-m','pip','download','--no-deps','--no-binary=:all:',
    '--dest',str(sources),'esptool==4.12.0','pyserial==3.5'],check=True)
with zipfile.ZipFile(root/'dist'/f'PlayOS-Installer-{sys.platform}.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in package.rglob('*'):
        if path.is_file(): archive.write(path,path.relative_to(package.parent))
