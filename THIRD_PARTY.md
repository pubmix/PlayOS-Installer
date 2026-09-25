# Third-party software

Installer: GPL-3.0-or-later; full source accompanies this release.

Bundled components:

- Python 3.12 and Tcl/Tk: PSF and Tcl/Tk licenses; PyInstaller includes their runtime notices.
- esptool 4.12.0: GPL-2.0-or-later. https://github.com/espressif/esptool/tree/v4.12.0
- pyserial 3.5: BSD. https://github.com/pyserial/pyserial/tree/v3.5
- Other esptool dependencies include bitstring, bitarray, cryptography/OpenSSL, cffi, pycparser, ecdsa, six, reedsolo, PyYAML and intelhex. Their exact versions, package metadata and supplied license notices are under licenses/python-packages.
- openFPGALoader 1.0.0: Apache-2.0. https://github.com/trabucayre/openFPGALoader/tree/v1.0.0
- libusb 1.0.30 and libftdi 1.5: LGPL-2.1-or-later, dynamically linked. Their matching source archives and MSYS2 build recipes are included in the source download. Replace DLLs in installer/tools and run build.py to rebuild with modified libraries.
- GCC runtime libraries: GPL-3.0-or-later with GCC Runtime Library Exception 3.1.
- winpthreads: mingw-w64 license; zlib: zlib license.

See licenses/ for copied notices and tools/packages.json for exact MSYS2 package URLs and verified checksums. Only the runtime DLLs required by openFPGALoader are shipped. Additional package metadata can list build-time or unused dependencies.

Firmware derives from ModRetro's GPL-3.0 Chromatic MCU and FPGA projects, with included modified source, upstream notices, the Gameboy_MiSTer source tree, LVGL, minimp3, and ESP-IDF patch instructions. Vendor-provided encrypted FPGA IP remains under its upstream terms and is included unchanged from the upstream project.

Gowin's proprietary programmer, USB driver installer, licenses, device backups, personal settings, and music files are not included. The USB setup link opens ModRetro's official updater page.
