# Publishing ChromaPlayer updates

Permanent public page: **https://github.com/pubmix/PlayOS-Installer/releases**

Share that page instead of a URL containing a specific version. It displays published updates, including alpha releases. Visitors do not need a GitHub account to download. The `pubmix` account owns the repository and has administrator access.

## Easiest: use GitHub

1. Build and test the updated installer using the complete source archive's `BUILDING.md`. Include the matching firmware source and regenerate checksums. Use a new version, such as `v0.2.0-alpha.2`.
2. Open [Create a new release](https://github.com/pubmix/PlayOS-Installer/releases/new).
3. Choose a new tag for that version and select the commit containing its installer changes.
4. Add a title and describe what changed and what was tested.
5. Attach the installer, matching source ZIP, firmware ZIP, `SHA256SUMS.txt`, and `VALIDATION.md`.
6. Keep **Set as a pre-release** checked while the release remains experimental. Publish the release.

The same public page now shows the new version. Keep the executable asset name **ChromaPlayer-Installer.exe** so people know which file to download. Do not replace an already-published version's binaries; publish a new version so old checksums and rollback references remain valid.

## One command

Install Python and GitHub CLI, authenticate with `gh auth login`, and run this from the installer repository:

```powershell
python publish_release.py v0.2.0-alpha.2 --assets C:\path\to\release-files --notes C:\path\to\release-notes.md --target YOUR_COMMIT_SHA --publish
```

Replace the example version and commit SHA with the actual version and pushed commit. The files directory must contain:

```text
ChromaPlayer-Installer.exe
ChromaPlayer-Source-v0.2.0-alpha.2.zip
ChromaPlayer-Firmware-v0.2.0-alpha.2.zip
SHA256SUMS.txt
VALIDATION.md
```

`SHA256SUMS.txt` must have a SHA-256 entry for each of the four other files. The command validates the hashes, creates a draft, uploads the assets, then publishes it as a prerelease. A failed upload leaves a draft; rerunning with the same version can finish that draft. It refuses to overwrite an already-public version.

- Omit `--publish` to leave a draft for review.
- Add `--dry-run` to check local files without contacting GitHub.
- Add `--stable` only after the release is qualified; stable releases can use GitHub's “Latest” designation. Alpha versions must remain prereleases.

This command publishes files you have already built. It does not build firmware, sign the EXE, or flash devices. Record the actual tests in `VALIDATION.md`. Never package device backups, personal NVS/settings, credentials, or music files.
