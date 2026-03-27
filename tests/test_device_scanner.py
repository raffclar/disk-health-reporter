import unittest
from unittest.mock import MagicMock, patch

from disk_health_reporter.device_scanner import get_block_devices


class TestDeviceScanner(unittest.TestCase):

    @patch("disk_health_reporter.device_scanner.os.path.exists")
    @patch("disk_health_reporter.device_scanner.subprocess.run")
    def test_get_block_devices_success(self, mock_run, mock_exists):
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="sda\nnvme0n1\nloop0\nram0\n",
            stderr=""
        )

        devices = get_block_devices()

        # Correcting expectation as we fixed the bug
        self.assertEqual(len(devices), 2)
        self.assertIn("/dev/sda", devices)
        self.assertIn("/dev/nvme0n1", devices)

    @patch("disk_health_reporter.device_scanner.os.path.exists")
    def test_get_block_devices_no_dev(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(RuntimeError) as cm:
            get_block_devices()
        self.assertEqual(str(cm.exception), "The /dev directory does not exist")
