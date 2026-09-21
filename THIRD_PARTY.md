# Third-party components

- Installer source: GPL-3.0-or-later; full source is in this repository.
- esptool 4.12.0: GPL-2.0-or-later, https://github.com/espressif/esptool/tree/v4.12.0 . Bundled in Windows builds; source and licenses are included under third-party-source.
- pyserial 3.5: BSD, https://github.com/pyserial/pyserial/tree/v3.5 . Python source distribution included in Windows release.
- Python: PSF license, https://www.python.org/ . PyInstaller bundles the interpreter and Tk dependencies.
- PyInstaller 6.16.0: GPL with bootloader exception, https://pyinstaller.org/ . Build dependency.
- Gowin Programmer/GWU2X drivers: separately installed vendor software, not redistributed here.
- openFPGALoader: Apache-2.0, https://github.com/trabucayre/openFPGALoader . Separately installed, not bundled.

ChromaPlayer MCU and FPGA sources derive from GPL-3.0 repositories. This release does not redistribute their binaries or private changes. The local development firmware pack is intentionally excluded from Git and release archives.
