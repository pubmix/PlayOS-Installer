"""Windows ChromaPlayer installer UI. GPL-3.0-or-later."""
import sys
import shutil

# A console-capable executable also serves as the isolated esptool subprocess.
if '--esptool' in sys.argv:
    import esptool
    esptool.main(sys.argv[sys.argv.index('--esptool')+1:])
    raise SystemExit

import queue
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from flasher import Flasher, verify_pack

if '--check-only' in sys.argv:
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--programmer',required=True)
    parser.add_argument('--firmware',required=True)
    parser.add_argument('--backend',choices=['gowin','openfpgaloader'],default='gowin')
    args=parser.parse_args()
    Flasher(args.programmer,args.firmware,print,lambda n,s:print(s),args.backend).check()
    print('CHECK PASSED: no firmware written')
    raise SystemExit

def main():
    root=tk.Tk(); root.title('PlayOS Installer — experimental'); root.geometry('800x650')
    base=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent
    events=queue.Queue(); state={'busy':False,'engine':None,'log':[]}
    backend='gowin' if sys.platform=='win32' else 'openfpgaloader'
    default_programmer='C:/Gowin/Gowin_V1.9.12.03_x64/Programmer/bin/programmer_cli.exe' if backend=='gowin' else shutil.which('openFPGALoader') or ('/opt/homebrew/bin/openFPGALoader' if sys.platform=='darwin' else '/usr/bin/openFPGALoader')
    programmer=tk.StringVar(value=default_programmer)
    folder=tk.StringVar(value=str(base/'firmware'))
    confirmed=tk.BooleanVar(value=False); status=tk.StringVar(value='Connect ONE powered-on Chromatic with a USB data cable.')
    frame=ttk.Frame(root,padding=16); frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='PlayOS Installer',font=('Segoe UI',20,'bold')).pack(anchor='w')
    ttk.Label(frame,text='Install ChromaPlayer • Experimental • PCB 100-0171-08 only',foreground='#9b3900').pack(anchor='w')
    ttk.Label(frame,text='Replaces stock firmware. No automatic backup or guaranteed rollback.\nKeep power and USB connected until finished. Online features currently require the developer’s LAN server.',wraplength=740).pack(anchor='w',pady=8)
    entries=[]
    def row(label,var,browse):
        ttk.Label(frame,text=label).pack(anchor='w')
        line=ttk.Frame(frame); line.pack(fill='x',pady=3)
        entry=ttk.Entry(line,textvariable=var); entry.pack(side='left',fill='x',expand=True); entries.append(entry)
        button=ttk.Button(line,text='Browse',command=lambda:var.set(browse() or var.get())); button.pack(side='right'); entries.append(button)
    row('Gowin programmer_cli.exe + GWU2X driver' if backend=='gowin' else 'openFPGALoader executable (GWU2X support required; hardware validation pending)',programmer,filedialog.askopenfilename)
    row('Firmware pack folder',folder,filedialog.askdirectory)
    checkbox=ttk.Checkbutton(frame,text='I confirm PCB revision 100-0171-08 and accept replacing its firmware.',variable=confirmed)
    checkbox.pack(anchor='w',pady=8); entries.append(checkbox)
    controls=ttk.Frame(frame); controls.pack(fill='x')
    def log(text): events.put(('log',text))
    def progress(n,text): events.put(('progress',(n,text)))
    def worker(action):
        try:
            action(); events.put(('done',None))
        except Exception as error: events.put(('error',str(error)))
    def start(action):
        state['busy']=True
        for widget in entries+[check,install]: widget.configure(state='disabled')
        threading.Thread(target=worker,args=(action,),daemon=True).start()
    def check_action():
        state['engine']=Flasher(programmer.get(),folder.get(),log,progress,backend)
        start(state['engine'].check)
    def install_action():
        engine=state['engine']
        if not confirmed.get(): messagebox.showwarning('Board confirmation','Confirm the PCB revision first.'); return
        if not engine or not engine.mac or engine.programmer!=str(Path(programmer.get()).resolve()) or engine.folder!=Path(folder.get()).resolve():
            messagebox.showwarning('Check required','Run Check device with the selected tools and firmware first.'); return
        if not messagebox.askyesno('Replace firmware?',f'Flash Chromatic {engine.mac}?\n\nFPGA first, then ESP32. Existing stock firmware will be replaced. No verified backup is available from this installer. Do not interrupt.'):
            return
        start(engine.install)
    check=ttk.Button(controls,text='1. Check device',command=check_action); check.pack(side='left')
    install=ttk.Button(controls,text='2. Install ChromaPlayer',command=install_action); install.pack(side='left',padx=8)
    def save():
        destination=filedialog.asksaveasfilename(defaultextension='.txt',initialfile='chromaplayer-install-log.txt')
        if destination: Path(destination).write_text('\n'.join(state['log']),encoding='utf-8')
    ttk.Button(controls,text='Save log',command=save).pack(side='right')
    bar=ttk.Progressbar(frame,maximum=4); bar.pack(fill='x',pady=10)
    ttk.Label(frame,textvariable=status,wraplength=740).pack(anchor='w')
    output=tk.Text(frame,height=17,wrap='word',state='disabled'); output.pack(fill='both',expand=True,pady=8)
    def pump():
        while not events.empty():
            kind,value=events.get()
            if kind=='log':
                state['log'].append(value); output.configure(state='normal'); output.insert('end',value+'\n'); output.see('end'); output.configure(state='disabled')
            elif kind=='progress': bar['value']=value[0]; status.set(value[1])
            else:
                state['busy']=False
                for widget in entries+[check,install]: widget.configure(state='normal')
                if kind=='error':
                    status.set('Stopped: '+value); state['log'].append('ERROR: '+value)
                    messagebox.showerror('Installation stopped',value+'\n\nDo not blindly retry or unplug during a tool operation. Save the log. See README recovery notes.')
        root.after(100,pump)
    def close():
        if state['busy']: messagebox.showwarning('Operation running','Wait for the operation to finish before closing.'); return
        root.destroy()
    root.protocol('WM_DELETE_WINDOW',close); pump()
    if '--smoke-test' in sys.argv:
        root.update(); print('GUI initialized: '+root.title()); root.after(200,root.destroy)
    root.mainloop()

if __name__=='__main__': main()
