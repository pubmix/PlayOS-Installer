# v0.1.0-alpha.1 — PlayOS Installer

Initial experimental installer release.

- Windows x64: extract ZIP and run PlayOS-Installer.exe. Python/esptool bundled; install Gowin Programmer V1.9.12.03 and GWU2X driver separately.
- macOS: experimental source launcher; Python with Tk and openFPGALoader required. Run bash Start-macOS.command.
- Linux: experimental source launcher; Python/venv/Tk, USB permissions and openFPGALoader required. Run sh start-linux.sh.

**No ChromaPlayer firmware is included.** Select a separately obtained trusted revision-08 firmware pack. Private firmware, source modifications, and local-server configuration have not been published by this release.

Safety: explicit confirmation, one-device checks, file hashes and size limits, FPGA-first ordering, verification gates, ESP32 identity recheck, error logs, and no full-chip erase. No automatic recovery backup. Do not interrupt flashing.

Validation: eight safety tests passed; Windows executable launched its GUI and successfully ran packaged esptool and Gowin hardware preflight without flashing. Complete installation through this GUI remains unqualified; underlying Windows programming commands were previously used successfully on two boards. Mac/Linux backend commands are implemented and mock-tested but have not been run on physical Mac/Linux hardware. Packages are unsigned.
