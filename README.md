# ChromaPlayer Installer

A single-file Windows app for installing ChromaPlayer on a ModRetro Chromatic **PCB 100-0171-08**.

**[Download ChromaPlayer for Windows](https://github.com/pubmix/PlayOS-Installer/releases/download/v0.2.0-alpha.1/ChromaPlayer-Installer.exe)**

This is an **experimental alpha**, not an official ModRetro product. Windows 10/11 x64 only. The full installation sequence has not yet been qualified on hardware with this release.

## Install

1. Download and open `ChromaPlayer-Installer.exe`. No ZIP extraction, Python, command line, Gowin Designer, or separate firmware selection is needed.
2. Connect **one** Chromatic using a USB data cable and turn it on.
3. Confirm that your board is **100-0171-08**, then click **Install ChromaPlayer**.
4. Leave USB and power connected until the app reports verification complete. Check for the Pubmix splash on the handheld.

If the device is not detected, use **USB setup help** in the app. A computer that has never used the Chromatic programmer may need the **GWU2X USB driver** supplied with [ModRetro's official updater](https://support.modretro.com/en_us/chromatic-firmware-updater-ryhoYnzCx). Driver setup may require Windows administrator approval. The driver installer is not bundled. Close the official updater before using this app.

The PCB revision is printed on the circuit board. A detected FPGA ID does **not** prove the PCB revision. Do not install on an unknown or different revision.

## What the app does

- Includes the firmware, openFPGALoader, esptool, and Python runtime.
- Checks firmware hashes, tools, connected-device count, FPGA ID, and ESP32 identity.
- Installs and verifies FPGA firmware **before** installing the MCU firmware.
- Stops if a stage fails, verification is incomplete, or the device changes.
- Writes logs to `%LOCALAPPDATA%\ChromaPlayer\Logs` and includes a **Save log** button.
- Keeps advanced file and programmer choices out of the normal flow.

Factory firmware is replaced. There is **no automatic backup or rollback**. The installer does not issue a full-chip erase and does not target NVS or SD-card contents. Interrupted flashing can leave a partial installation. Save the log and use the correct recovery procedure; stock recovery requires **MCU first, FPGA second**.

## Release limits

- This executable is unsigned. Signing and a clean-computer installation qualification are still outstanding.
- Software tests, packaged-runtime checks, and read-only FPGA detection are completed; a full flash through this release is not.
- The firmware source snapshot includes SD playback, Bluetooth, Wi-Fi and messaging work. This is a development firmware snapshot, not a promise that every feature is production-ready.
- The library/sync endpoint is still the development LAN address `http://192.168.1.84:8765`; that feature is not portable in this snapshot. SD playback does not require that server. Messaging uses the existing pubmix.com service.
- macOS/Linux native downloads are not provided by this release.

## Source and checksums

The [release page](https://github.com/pubmix/PlayOS-Installer/releases/tag/v0.2.0-alpha.1) includes the complete installer/firmware source snapshot, relevant dependency source archives, a standalone firmware pack, and SHA-256 checksums. Build instructions and provenance are inside the source archive. No personal device backups, Wi-Fi credentials, music collection, or NVS images are included.

The original firmware-free v0.1.0 release remains available for historical reference.

For a complete rebuild, use the source archive attached to the release. This Git repository contains the installer code; the archive additionally supplies the corresponding firmware source, images, runtime binaries, notices, and build instructions.
