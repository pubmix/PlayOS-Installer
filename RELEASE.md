# ChromaPlayer Installer v0.2.0-alpha.1

Download **ChromaPlayer-Installer.exe**, connect one supported Chromatic, confirm PCB **100-0171-08**, and click **Install ChromaPlayer**.

This release includes firmware and both flashing tools in a single Windows executable. No ZIP extraction, Python installation, command line, Gowin application, or separate firmware selection is needed. A first-time computer may still need the GWU2X USB driver; the app links to ModRetro's official setup page.

The installer checks firmware checksums and device identity, programs and verifies the FPGA first, then programs and verifies the MCU. Incomplete verification or a changed device stops the process. Logs are saved automatically.

## Downloads

- **ChromaPlayer-Installer.exe** — Windows 10/11 x64 app with firmware included.
- **ChromaPlayer-Source-v0.2.0-alpha.1.zip** — corresponding MCU/FPGA source, installer source, build instructions, provenance and dependency source packages.
- **ChromaPlayer-Firmware-v0.2.0-alpha.1.zip** — firmware pack for developers; ordinary users only need the EXE.
- **SHA256SUMS.txt** — SHA-256 checksums.
- **VALIDATION.md** — completed checks and remaining qualification.

## Alpha limitations

This release is unsigned and experimental. Software checks and read-only FPGA detection passed, but a complete installation through this release and clean-Windows qualification remain outstanding. Factory firmware is replaced; automatic backup/rollback is not available. Keep USB and power connected during installation.

The library/sync feature still uses a development LAN server; it is not portable in this firmware snapshot. SD playback does not require that server. Messaging uses pubmix.com. Only PCB 100-0171-08 is supported; other boards and macOS/Linux are not qualified by this release.

Independent project, not an official ModRetro product.
