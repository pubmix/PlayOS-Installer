# PlayOS Installer

An experimental desktop installer for ChromaPlayer on the ModRetro Chromatic.
Independent project; not an official ModRetro product. Supported PCB target: **100-0171-08 only**.

## Important: bring a firmware pack

This public repository and its downloads contain the **installer, not ChromaPlayer firmware**.
The current firmware remains private and has local-server-dependent features. Publishing an installer does not make those services portable. Do not distribute firmware until its corresponding source, notices, branding/assets, and public server configuration have been reviewed for release.

Obtain a trusted compatible pack containing `manifest.json`, `fpga.fs`, `bootloader.bin`, `partitions.bin`, and `application.bin`. Select that directory in the app. The installer checks SHA-256 hashes for accidental corruption; an unsigned manifest is **not** proof of publisher authenticity. Never load an untrusted pack.

## Platform status

| Platform | Package | FPGA backend | Validation |
| --- | --- | --- | --- |
| Windows x64 | Standalone executable ZIP | Gowin Programmer V1.9.12.03 | 8 safety tests; packaged GUI smoke test; packaged device preflight passed on a real board. Full GUI installation not yet qualification-tested. Underlying flash commands previously verified on two boards. |
| macOS | Python launcher/source | openFPGALoader with GWU2X | Experimental; no physical Mac flash test yet |
| Linux | Python launcher/source | openFPGALoader with GWU2X | Experimental; no physical Linux flash test yet |

No claim of plug-and-play installation across every computer. No automated driver changes, security bypasses, or administrator elevation. Downloads are unsigned; do not bypass OS security warnings. Source launch is available for inspection and local execution.

## Windows

1. Download and extract the Windows ZIP from Releases. Keep the `_internal` directory alongside the executable.
2. Install [Gowin Programmer](https://www.gowinsemi.com/en/support/download_eda/) V1.9.12.03 and its GWU2X driver separately. They are not bundled. Designer is not needed to flash a prebuilt image.
3. Run `PlayOS-Installer.exe`; select `programmer_cli.exe` and your trusted firmware pack.
4. Connect **one** Chromatic with a USB data cable, switch it on, and confirm its PCB revision.
5. Click **Check device**. This verifies files, tools, FPGA identity and the ESP32 MAC; it can restart the handheld but does not write flash.
6. Click **Install ChromaPlayer**, confirm the displayed device, and do not unplug or power off during programming.
7. Success means the programming tools confirmed verification. Check that the handheld displays Pubmix; the installer does not automatically verify screen, audio, Wi-Fi, or SD behavior.

The executable includes esptool/Python components. A console window is retained for reliable tool subprocess execution; the graphical UI is separate.

## macOS

Install Python 3.12 with Tk support, then [openFPGALoader](https://trabucayre.github.io/openFPGALoader/guide/first-steps.html) (`brew install openfpgaloader`). Your openFPGALoader build must support the Gowin GWU2X cable.

Run `bash Start-macOS.command` from the extracted source folder. The launcher creates a local `.runtime` environment and installs the pinned Python dependencies from PyPI. On Apple Silicon, the default tool path is `/opt/homebrew/bin/openFPGALoader`; use Browse for another installation.

## Linux

Install Python 3.12-compatible Python, venv, Tk, openFPGALoader, and the USB access rules recommended by [upstream](https://trabucayre.github.io/openFPGALoader/guide/install.html). Distribution package names vary (often `python3-venv` and `python3-tk`). Your account needs access to both the serial and GWU2X interfaces. Do not run the installer as root just to avoid diagnosing USB permissions.

Run `sh start-linux.sh`. It creates `.runtime` and installs the pinned Python dependencies. Use Browse to select openFPGALoader if it is not on PATH.

Both non-Windows backends require `--verify`, use external-flash programming, and stop before MCU flashing if verification is not reported. macOS/Linux need physical qualification before a stable release. Upstream [GW5 external-flash implementation](https://github.com/trabucayre/openFPGALoader/blob/master/src/gowin.cpp) calls SPI flash verification; this is different from its internal-flash path, which does not support verification.

## Safety and recovery

- FPGA is installed and verified **before** MCU. Stock FPGA and custom MCU audio pin directions differ.
- Exactly one serial device and compatible FPGA are required. ESP32 identity is rechecked before writing and after FPGA reset.
- Application size is bounded to the supported partition. MCU writes target 0x1000 (bootloader), 0x8000 (partition table), and 0x10000 (application). NVS at 0x9000 and SD contents are not erased by these commands.
- No guaranteed backup/rollback: earlier stock readback attempts on our hardware failed. This is not a factory-preserving installation.
- If a tool fails, later stages stop. Save the log. Do not assume a partial installation is bootable. Restoring stock requires the correct official images and **MCU first, FPGA second**. Follow the official recovery procedure for your board, not random images.
- Do not close the program while flashing. USB loss or forced process termination can still leave a partial installation.

## Development

```text
python -m venv .venv
# Activate .venv using the convention for your OS.
python -m pip install -r requirements.txt
python -m pip install pyinstaller==6.16.0
python -m unittest -v
python app.py
python build.py
```

Build on each target OS; PyInstaller is not a cross-compiler. No firmware is added by `build.py`. Mac/Linux launchers are the initial release format; native frozen bundles can be produced on those platforms with the same script. GPL-3.0-or-later; see LICENSE and THIRD_PARTY.md.
