"""ChromaPlayer Windows installer. GPL-3.0-or-later."""
import os
import queue
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from flasher import Flasher, verify_pack

BASE = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
RELEASE_URL = 'https://github.com/pubmix/PlayOS-Installer/releases/tag/v0.2.0-alpha.1'
DRIVER_URL = 'https://support.modretro.com/en_us/chromatic-firmware-updater-ryhoYnzCx'

if '--self-test' in sys.argv:
    import json
    from flasher import esp_command
    report = Path(sys.argv[sys.argv.index('--self-test') + 1])
    try:
        engine = Flasher(BASE/'tools'/'openFPGALoader.exe', BASE/'firmware', lambda _: None, lambda *_: None, 'openfpgaloader')
        manifest = verify_pack(BASE/'firmware')
        help_text = engine.run([engine.programmer, '--help'], 30)
        cables = engine.run([engine.programmer, '--list-cables'], 30)
        esp = engine.run(esp_command(['version']), 30)
        assert '--verify' in help_text and 'gwu2x' in cables and '4.12.0' in esp
        report.write_text(json.dumps({'passed': True, 'firmware': manifest['version'], 'checks': ['firmware hashes', 'bundled FPGA tool and DLLs', 'GWU2X support', 'bundled esptool 4.12.0']}, indent=2))
    except Exception as error:
        report.write_text(json.dumps({'passed': False, 'error': str(error)}, indent=2))
        raise SystemExit(1)
    raise SystemExit

def main():
    root = tk.Tk()
    root.title('ChromaPlayer Installer')
    root.geometry('720x630')
    root.minsize(660, 580)
    root.configure(bg='#f5f6fa')
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background='#f5f6fa')
    style.configure('TLabel', background='#f5f6fa', foreground='#20263b', font=('Segoe UI', 10))
    style.configure('TCheckbutton', background='#f5f6fa', font=('Segoe UI', 10))
    style.configure('TButton', font=('Segoe UI', 10), padding=8)
    style.configure('Install.TButton', font=('Segoe UI', 13, 'bold'), padding=12, background='#5748d9', foreground='white')
    style.map('Install.TButton', background=[('active', '#4336b2'), ('disabled', '#aaa6c8')])
    page = ttk.Frame(root, padding=26)
    page.pack(fill='both', expand=True)
    ttk.Label(page, text='ChromaPlayer', font=('Segoe UI', 27, 'bold')).pack(anchor='w')
    ttk.Label(page, text='Your music. Your Chromatic.', font=('Segoe UI', 13)).pack(anchor='w', pady=(0, 16))
    ttk.Label(page, text='1   Plug in one Chromatic with a USB data cable.\n2   Turn it on and confirm the board below.\n3   Install, then keep USB and power connected until done.', justify='left').pack(anchor='w')
    ttk.Label(page, text='EXPERIMENTAL • WINDOWS 10/11 x64 • BOARD 100-0171-08', foreground='#81531b', font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(15, 3))
    ttk.Label(page, text='Replaces factory firmware. Automatic rollback is not available.\nThis release has not completed an end-to-end installation test.', wraplength=655).pack(anchor='w')
    consent = tk.BooleanVar()
    checkbox = ttk.Checkbutton(page, text='My board is 100-0171-08. I agree to replace its firmware.', variable=consent)
    checkbox.pack(anchor='w', pady=12)
    firmware = tk.StringVar(value=str(BASE / 'firmware'))
    programmer = tk.StringVar(value=str(BASE / 'tools' / 'openFPGALoader.exe'))
    backend = tk.StringVar(value='openfpgaloader')
    status = tk.StringVar(value='Ready. Firmware and flashing tools are included.')
    events = queue.Queue()
    state = {'busy': False, 'log': [], 'log_path': None, 'action': None}
    progressbar = ttk.Progressbar(page, maximum=4)
    progressbar.pack(fill='x', pady=5)
    ttk.Label(page, textvariable=status, wraplength=655).pack(anchor='w', pady=(3, 6))
    def log(text): events.put(('log', text))
    def progress(number, text): events.put(('progress', (number, text)))
    def launch(write):
        if state['busy']: return
        if write and not consent.get():
            messagebox.showinfo('Confirm your board', 'Confirm your board revision and firmware replacement above first.'); return
        engine = Flasher(programmer.get(), firmware.get(), log, progress, backend.get())
        state['busy'] = True
        state['action'] = 'install' if write else 'check'
        state['log'] = []
        details.configure(state='normal'); details.delete('1.0', 'end'); details.configure(state='disabled')
        for control in editable: control.configure(state='disabled')
        status.set('Checking your device and firmware…')
        progressbar['value'] = 0
        try:
            log_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'ChromaPlayer' / 'Logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            state['log_path'] = log_dir / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.log')
        except OSError: state['log_path'] = None
        def worker():
            try:
                engine.check()
                if write: engine.install()
                events.put(('done', write))
            except Exception as error: events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()
    install = ttk.Button(page, text='Install ChromaPlayer', style='Install.TButton', command=lambda: launch(True))
    install.pack(fill='x', pady=8)
    links = ttk.Frame(page)
    links.pack(fill='x')
    check = ttk.Button(links, text='Check connection only', command=lambda: launch(False))
    check.pack(side='left')
    ttk.Button(links, text='USB setup help', command=lambda: messagebox.showinfo('First-time USB setup',
        'If your device is not detected:\n\n1. Try a USB data cable and turn the Chromatic on.\n2. Connect only one Chromatic. Close other updaters.\n3. Install the GWU2X USB driver supplied with ModRetro’s official updater. You do not need Gowin Designer.\n\nUse the Official driver page button below. Do not start an official firmware update while this installer is running.')).pack(side='left', padx=5)
    ttk.Button(links, text='Official driver page', command=lambda: webbrowser.open(DRIVER_URL)).pack(side='left')
    advanced = ttk.Frame(page)
    def toggle():
        if advanced.winfo_manager(): advanced.pack_forget(); root.geometry('720x630')
        else: advanced.pack(fill='x', before=details, pady=5); root.geometry('720x760')
    ttk.Button(page, text='Advanced options / recovery tools', command=toggle).pack(anchor='w', pady=5)
    editable = [install, check, checkbox]
    for label, var, picker in (
        ('Programmer', programmer, filedialog.askopenfilename),
        ('Firmware folder', firmware, filedialog.askdirectory)):
        row = ttk.Frame(advanced); row.pack(fill='x', pady=2)
        ttk.Label(row, text=label, width=15).pack(side='left')
        entry = ttk.Entry(row, textvariable=var); entry.pack(side='left', fill='x', expand=True)
        button = ttk.Button(row, text='Browse', command=lambda v=var, p=picker: v.set(p() or v.get()))
        button.pack(side='left'); editable.extend((entry, button))
    backend_select = ttk.Combobox(advanced, textvariable=backend, values=['openfpgaloader', 'gowin'], state='readonly')
    backend_select.pack(anchor='w'); editable.append(backend_select)
    details = tk.Text(page, height=5, wrap='word', font=('Consolas', 9), state='disabled', bg='white', relief='flat')
    details.pack(fill='both', expand=True, pady=5)
    footer = ttk.Frame(page); footer.pack(fill='x')
    def save():
        target = filedialog.asksaveasfilename(initialfile='ChromaPlayer-install.log', defaultextension='.log')
        if target: Path(target).write_text('\n'.join(state['log']), encoding='utf-8')
    ttk.Button(footer, text='Save log', command=save).pack(side='right')
    ttk.Button(footer, text='Release notes & source', command=lambda: webbrowser.open(RELEASE_URL)).pack(side='left')
    def record(text):
        state['log'].append(text)
        details.configure(state='normal'); details.insert('end', text + '\n'); details.see('end'); details.configure(state='disabled')
        if state['log_path']:
            try:
                with state['log_path'].open('a', encoding='utf-8') as file: file.write(text + '\n')
            except OSError: state['log_path'] = None
    def pump():
        while not events.empty():
            kind, value = events.get()
            if kind == 'log': record(value)
            elif kind == 'progress': progressbar['value'] = value[0]; status.set(value[1])
            else:
                state['busy'] = False
                for control in editable: control.configure(state='normal')
                backend_select.configure(state='readonly')
                if kind == 'error':
                    record('STOPPED: ' + value)
                    status.set('Stopped. Details are saved in your installation log.')
                    messagebox.showerror('Installation stopped', value + '\n\nNo later stage was run. Use USB setup help for detection problems. Save the log before recovery.')
                else:
                    text = 'Installation verified. Check the Pubmix splash on your handheld.' if value else 'Connection checks passed. Ready to install.'
                    record(text); status.set(text)
        root.after(100, pump)
    def close():
        if state['busy']: messagebox.showinfo('Please wait', 'Keep the installer open and USB connected until the operation finishes.')
        else: root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    pump()
    if '--smoke-test' in sys.argv: root.after(300, root.destroy)
    root.mainloop()

if __name__ == '__main__': main()
