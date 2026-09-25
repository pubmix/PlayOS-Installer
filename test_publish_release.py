import hashlib
from pathlib import Path
import tempfile
import unittest
from publish_release import validate

class ReleaseValidationTests(unittest.TestCase):
    def fixture(self, root):
        names=['ChromaPlayer-Installer.exe','ChromaPlayer-Source-v1.0.0.zip',
               'ChromaPlayer-Firmware-v1.0.0.zip','VALIDATION.md']
        for name in names: (root/name).write_bytes(b'release fixture')
        lines=[hashlib.sha256((root/name).read_bytes()).hexdigest()+'  '+name for name in names]
        (root/'SHA256SUMS.txt').write_text('\n'.join(lines))

    def test_accepts_matching_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            self.assertEqual(len(validate('v1.0.0',root)),5)

    def test_rejects_changed_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            (root/'ChromaPlayer-Installer.exe').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'SHA-256'): validate('v1.0.0',root)

    def test_rejects_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            (root/'ChromaPlayer-Source-v1.0.0.zip').unlink()
            with self.assertRaisesRegex(ValueError,'Missing or empty'): validate('v1.0.0',root)

    def test_rejects_path_in_version(self):
        with self.assertRaises(ValueError): validate('../v1.0.0','.')

if __name__=='__main__': unittest.main()
