"""ChromaPlayer installer engine. GPL-3.0-or-later. No shell execution."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

FILES = ('fpga.fs', 'bootloader.bin', 'partitions.bin', 'application.bin')

def verify_pack(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest.get('schema') != 1 or manifest.get('board') != '100-0171-08':
        raise RuntimeError('Unsupported firmware manifest or board revision.')
    for name in FILES:
        expected = manifest.get('sha256', {}).get(name, '')
        if not re.fullmatch(r'[a-fA-F0-9]{64}', expected):
            raise RuntimeError('Missing checksum: ' + name)
        path = (folder / name).resolve()
        if path.parent != folder or not path.is_file():
            raise RuntimeError('Missing or unsafe firmware file: ' + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected.lower():
            raise RuntimeError('Checksum mismatch: ' + name)
    if (folder/'application.bin').stat().st_size > 0x2f0000:
        raise RuntimeError('Application exceeds the fixed supported partition.')
    if (folder/'bootloader.bin').stat().st_size>0x7000 or (folder/'partitions.bin').stat().st_size>0x1000:
        raise RuntimeError('Bootloader or partition image would overwrite reserved storage.')
    return manifest

def single_port():
    from serial.tools import list_ports
    ports = [p.device for p in list_ports.comports() if p.vid == 0x374e]
    if len(ports) != 1:
        raise RuntimeError(f'Expected one Chromatic; found {len(ports)}. Connect only one, powered on.')
    return ports[0]

def esp_command(args):
    if getattr(sys, 'frozen', False):
        return [sys.executable, '--esptool', *args]
    return [sys.executable, '-m', 'esptool', *args]

def mcu_command(port, folder):
    folder = Path(folder).resolve()
    return esp_command(['--chip','esp32','-p',port,'-b','460800',
        '--before','default_reset','--after','hard_reset','write_flash',
        '--flash_mode','dio','--flash_freq','40m','--flash_size','4MB',
        '0x1000',str(folder/'bootloader.bin'),'0x8000',str(folder/'partitions.bin'),
        '0x10000',str(folder/'application.bin')])

class Flasher:
    def __init__(self, programmer, folder, log, progress, backend='gowin'):
        self.programmer = str(Path(programmer).resolve())
        self.folder = Path(folder).resolve()
        self.log, self.progress = log, progress
        self.mac = None
        if backend not in ('gowin','openfpgaloader'): raise ValueError('Unknown backend')
        self.backend=backend

    def run(self, args, timeout=180):
        # Capture to disk to avoid pipe deadlocks and retain diagnostics if USB fails.
        import tempfile
        self.log('Running: ' + Path(args[0]).name + ' ' + ' '.join(args[1:]))
        with tempfile.TemporaryDirectory() as temporary, open(Path(temporary)/'tool.log','wb') as writer, open(Path(temporary)/'tool.log','rb') as capture:
            external=getattr(sys,'frozen',False) and Path(args[0]).resolve()!=Path(sys.executable).resolve()
            env=os.environ.copy()
            if external:
                # Do not inject our frozen Python/DLL environment into Gowin's
                # own embedded Python, or system libraries into openFPGALoader.
                for key in list(env):
                    if key.startswith(('_PYI','_MEIPASS')) or key in ('PYTHONHOME','PYTHONPATH'):
                        env.pop(key,None)
                for key in ('LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'):
                    if key+'_ORIG' in env: env[key]=env[key+'_ORIG']
                    else: env.pop(key,None)
            reset_dll=external and sys.platform=='win32'
            if reset_dll:
                import ctypes
                ctypes.windll.kernel32.SetDllDirectoryW(None)
            try:
                process = subprocess.Popen(args, stdout=writer, stderr=subprocess.STDOUT,env=env,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            finally:
                if reset_dll: ctypes.windll.kernel32.SetDllDirectoryW(sys._MEIPASS)
            start=time.monotonic(); position=0; chunks=[]
            while True:
                time.sleep(.15)
                capture.seek(position); data=capture.read(); position+=len(data)
                if data:
                    chunk=data.decode('utf-8',errors='replace'); chunks.append(chunk); self.log(chunk)
                if process.poll() is not None:
                    capture.seek(position); chunk=capture.read().decode('utf-8',errors='replace')
                    chunks.append(chunk)
                    if chunk: self.log(chunk)
                    break
                if time.monotonic()-start>timeout:
                    process.kill(); process.wait()
                    raise RuntimeError('Tool timed out. Do not unplug; save the log and use recovery instructions.')
        result=''.join(chunks)
        if process.returncode:
            raise RuntimeError(f'{Path(args[0]).name} failed ({process.returncode}). See log; no later stage was run.')
        return result

    def gowin(self, operation):
        return [self.programmer,'--device','GW5A-25A','--cable-index','0',
                '--operation_index',str(operation)]

    def identify(self):
        port=single_port()
        output=self.run(esp_command(['--chip','esp32','-p',port,'--before','default_reset',
                        '--after','hard_reset','read_mac']),30)
        match=re.search(r'MAC:\s*([0-9a-fA-F:]{17})',output)
        if not match: raise RuntimeError('ESP32 identity could not be verified.')
        return match.group(1).lower()

    def check(self):
        self.progress(0,'Checking files and tools')
        verify_pack(self.folder)
        if not Path(self.programmer).is_file(): raise RuntimeError('Select Gowin programmer_cli.exe first.')
        help_text=self.run([self.programmer,'--help'],30)
        if self.backend=='gowin' and 'V1.9.12.03' not in help_text:
            raise RuntimeError('This installer is tested with Gowin Programmer V1.9.12.03 only.')
        if self.backend=='openfpgaloader' and '--verify' not in help_text:
            raise RuntimeError('openFPGALoader must support --verify and the GWU2X cable.')
        self.mac=self.identify()
        scan=self.run([self.programmer,'--scan','--cable-index','0'] if self.backend=='gowin' else [self.programmer,'--detect','--cable','gwu2x'],30)
        gowin_ok='1 device(s) found' in scan and '0x0001281B' in scan
        open_ids=re.findall(r'idcode\s*(?:[:=]\s*)?(0x[0-9a-f]+)',scan,re.I)
        open_ok=len(open_ids)==1 and int(open_ids[0],16)==0x1281b
        if not (gowin_ok if self.backend=='gowin' else open_ok):
            raise RuntimeError('Expected exactly one compatible Gowin FPGA; check power and GWU2X driver.')
        self.progress(0,'Ready: '+self.mac)
        return self.mac

    def install(self):
        # Recheck immediately before writing, including board identity after confirmation.
        original=self.mac
        if not original: raise RuntimeError('Run Check device before installing.')
        if self.check()!=original: raise RuntimeError('Device changed. Nothing flashed; check the intended unit again.')
        self.progress(1,'Installing FPGA — do not unplug')
        args=self.gowin(54)+['--fsFile',str(self.folder/'fpga.fs')] if self.backend=='gowin' else [self.programmer,'--cable','gwu2x','--write-flash','--verify',str(self.folder/'fpga.fs')]
        result=self.run(args)
        verified='Program and Verify Flash successfully' in result if self.backend=='gowin' else ('Verifying write' in result and not re.search(r'not supported|verification failed|failed to read|\bFAIL\b',result,re.I))
        if not verified:
            raise RuntimeError('FPGA verification not confirmed. MCU was NOT written.')
        self.progress(2,'Restarting FPGA')
        if self.backend=='gowin': self.run(self.gowin(1),30)
        # openFPGALoader reloads external flash unless --skip-reset is passed.
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            time.sleep(1)
            try:
                single_port(); break
            except RuntimeError: pass
        if self.identify()!=original:
            raise RuntimeError('Device identity changed after FPGA restart. MCU was NOT written.')
        self.progress(3,'Installing ESP32 firmware — do not unplug')
        result=self.run(mcu_command(single_port(),self.folder))
        if result.count('Hash of data verified') < 3:
            raise RuntimeError('Not all three MCU images reported verification. Save the log for recovery.')
        self.progress(4,'Flash verified. Confirm the Pubmix screen on the handheld.')
