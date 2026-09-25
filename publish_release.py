"""Validate and publish versioned ChromaPlayer releases. GPL-3.0-or-later."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

REPOSITORY = 'pubmix/PlayOS-Installer'

def validate(version, directory):
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?', version):
        raise ValueError('Use a version such as v0.2.0-alpha.2 or v0.2.0.')
    directory = Path(directory).resolve()
    names = ['ChromaPlayer-Installer.exe', f'ChromaPlayer-Source-{version}.zip',
             f'ChromaPlayer-Firmware-{version}.zip', 'VALIDATION.md']
    sums = directory / 'SHA256SUMS.txt'
    expected = {}
    for line in sums.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip(): continue
        match = re.fullmatch(r'([0-9a-fA-F]{64})\s+\*?([^/\\]+)', line)
        if not match or match[2] in expected:
            raise ValueError('Invalid or duplicate checksum line: ' + line)
        expected[match[2]] = match[1].lower()
    for name in names:
        path = directory / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError('Missing or empty release file: ' + name)
        with path.open('rb') as file: actual = hashlib.file_digest(file, 'sha256').hexdigest()
        if actual != expected.get(name): raise ValueError('Missing/mismatched SHA-256: ' + name)
    return [directory / name for name in names] + [sums]

def gh(*args):
    return subprocess.check_output(['gh', *args], text=True).strip()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version')
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--notes', type=Path, required=True)
    parser.add_argument('--target', required=True, help='Pushed commit SHA or branch for the release tag')
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--stable', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    files = validate(args.version, args.assets)
    if not args.notes.is_file() or not args.notes.read_text(encoding='utf-8').strip():
        raise ValueError('Provide non-empty release notes.')
    if args.stable and '-' in args.version:
        raise ValueError('An alpha/beta/rc version cannot be marked stable.')
    print('Validated all 5 release files.')
    if args.dry_run:
        print('Dry run complete. No GitHub changes.'); return
    # A failed API request is an error, never evidence that a release is absent.
    pages = json.loads(gh('api', '--paginate', '--slurp', f'repos/{REPOSITORY}/releases'))
    existing = next((release for page in pages for release in page if release['tag_name'] == args.version), None)
    if existing and not existing['draft']:
        raise ValueError('That version is already public. Choose a new version; published assets will not be replaced.')
    mode = ['--prerelease'] if not args.stable else []
    if not existing:
        gh('release', 'create', args.version, '--repo', REPOSITORY, '--draft', '--target', args.target,
           '--title', f'ChromaPlayer {args.version}', '--notes-file', str(args.notes.resolve()), *mode)
    else:
        gh('release', 'edit', args.version, '--repo', REPOSITORY, '--target', args.target,
           '--notes-file', str(args.notes.resolve()), '--prerelease=' + str(not args.stable).lower())
    gh('release', 'upload', args.version, *map(str, files), '--repo', REPOSITORY, '--clobber')
    uploaded_pages = json.loads(gh('api', '--paginate', '--slurp', f'repos/{REPOSITORY}/releases'))
    uploaded = next(release for page in uploaded_pages for release in page if release['tag_name'] == args.version)
    remote_hashes = {asset['name']: asset.get('digest') for asset in uploaded['assets']}
    for path in files:
        with path.open('rb') as file: digest = 'sha256:' + hashlib.file_digest(file, 'sha256').hexdigest()
        if remote_hashes.get(path.name) != digest:
            raise ValueError('Uploaded checksum could not be verified; release left as draft: ' + path.name)
    if args.publish:
        gh('release', 'edit', args.version, '--repo', REPOSITORY, '--draft=false',
           '--prerelease=' + str(not args.stable).lower(), '--latest=' + str(args.stable).lower())
    print(('Published: ' if args.publish else 'Draft ready: ') +
          f'https://github.com/{REPOSITORY}/releases/tag/{args.version}')

if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('Stopped: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
