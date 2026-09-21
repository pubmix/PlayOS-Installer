import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import flasher

class Tests(unittest.TestCase):
    def test_pack_rejects_tampering_and_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp); manifest={'schema':1,'board':'100-0171-08','sha256':{}}
            for name in flasher.FILES:
                (path/name).write_bytes(b'test'); manifest['sha256'][name]=hashlib.sha256(b'test').hexdigest()
            (path/'manifest.json').write_text(json.dumps(manifest))
            self.assertEqual(flasher.verify_pack(path)['board'],'100-0171-08')
            (path/'fpga.fs').write_bytes(b'changed')
            with self.assertRaisesRegex(RuntimeError,'Checksum'): flasher.verify_pack(path)
            manifest['board']='unknown'; (path/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(RuntimeError,'Unsupported'): flasher.verify_pack(path)

    def test_mcu_writes_only_supported_ranges(self):
        args=flasher.mcu_command('COM99','test folder')
        self.assertNotIn('erase_flash',args)
        self.assertNotIn('0x9000',args)
        self.assertTrue(all(offset in args for offset in ('0x1000','0x8000','0x10000')))

    def engine(self):
        e=flasher.Flasher('programmer.exe','pack',lambda _:None,lambda *_:None); e.mac='original'
        return e

    def test_failed_fpga_never_writes_mcu(self):
        e=self.engine()
        with patch.object(e,'check',return_value='original'), patch.object(e,'run',return_value='verification failed') as run:
            with self.assertRaisesRegex(RuntimeError,'MCU was NOT'): e.install()
            self.assertEqual(run.call_count,1)

    def test_swapped_device_blocks_before_write(self):
        e=self.engine()
        with patch.object(e,'check',return_value='different'), patch.object(e,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'Device changed'): e.install()
            run.assert_not_called()

    def test_order_and_verification(self):
        e=self.engine()
        with patch.object(e,'check',return_value='original'), patch.object(e,'identify',return_value='original'), patch('flasher.single_port',return_value='COM4'), patch('flasher.time.sleep'), patch.object(e,'run',side_effect=['Program and Verify Flash successfully','Finished','Hash of data verified\n'*3]) as run:
            e.install()
            calls=[c.args[0] for c in run.call_args_list]
            self.assertIn('54',calls[0]); self.assertIn('1',calls[1]); self.assertIn('write_flash',calls[2])

    def test_nonzero_tool_stops(self):
        import sys
        with self.assertRaisesRegex(RuntimeError,'failed'):
            self.engine().run([sys.executable,'-c','print("diagnostic"); raise SystemExit(2)'])

    def test_openfpgaloader_requires_verification(self):
        e=self.engine(); e.backend='openfpgaloader'
        with patch.object(e,'check',return_value='original'), patch.object(e,'run',return_value='writing verification not supported') as run:
            with self.assertRaisesRegex(RuntimeError,'MCU was NOT'): e.install()
            self.assertEqual(run.call_count,1)
            self.assertIn('--verify',run.call_args.args[0])

    def test_openfpgaloader_order(self):
        e=self.engine(); e.backend='openfpgaloader'
        with patch.object(e,'check',return_value='original'), patch.object(e,'identify',return_value='original'), patch('flasher.single_port',return_value='/dev/ttyACM0'), patch('flasher.time.sleep'), patch.object(e,'run',side_effect=['Verifying write (May take time)\nReading Done','Hash of data verified\n'*3]) as run:
            e.install()
            self.assertIn('--write-flash',run.call_args_list[0].args[0])
            self.assertIn('write_flash',run.call_args_list[1].args[0])

if __name__=='__main__': unittest.main()
