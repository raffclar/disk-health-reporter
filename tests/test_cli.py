import unittest
from unittest.mock import patch, MagicMock
from disk_health_reporter.cli import main, is_root

class TestCLI(unittest.TestCase):

    @patch("disk_health_reporter.cli.is_root")
    @patch("disk_health_reporter.cli.get_block_devices")
    @patch("disk_health_reporter.cli.get_smart_data")
    @patch("disk_health_reporter.cli.send_email_report")
    @patch("disk_health_reporter.cli.argparse.ArgumentParser.parse_args")
    @patch("disk_health_reporter.cli.console.print")
    def test_main_as_root_success(self, mock_print, mock_parse_args, mock_send_email, mock_get_smart, mock_get_devices, mock_is_root):
        mock_is_root.return_value = True
        mock_parse_args.return_value = MagicMock(
            email="test@example.com",
            from_email=None,
            smtp_server="localhost",
            smtp_port=25,
            smtp_user=None,
            smtp_pass=None,
            use_tls=False
        )
        mock_get_devices.return_value = ["/dev/sda"]
        mock_get_smart.return_value = {"device": "/dev/sda"}
        
        result = main()
        
        self.assertEqual(result, 0)
        mock_send_email.assert_called_once()
        # Verify it didn't print error about privileges
        for call in mock_print.call_args_list:
            self.assertNotIn("requires superuser", str(call))

    @patch("disk_health_reporter.cli.is_root")
    @patch("disk_health_reporter.cli.argparse.ArgumentParser.parse_args")
    @patch("disk_health_reporter.cli.console.print")
    def test_main_not_as_root_fails(self, mock_print, mock_parse_args, mock_is_root):
        mock_is_root.return_value = False
        mock_parse_args.return_value = MagicMock(email="test@example.com")
        
        result = main()
        
        self.assertEqual(result, 1)
        # Verify it printed error about privileges
        mock_print.assert_called_with("[bold red]Error: This tool requires superuser (root/administrator) privileges to run smartctl.[/bold red]")

    def test_is_root_linux_true(self):
        with patch("disk_health_reporter.cli.os") as mock_os:
            mock_os.geteuid.return_value = 0
            mock_os.hasattr.side_effect = lambda obj, name: name == "geteuid"
            # Since hasattr is a builtin, we might need to mock it differently or 
            # just mock how it's used in is_root. 
            # In cli.py: if hasattr(os, "geteuid"): return os.geteuid() == 0
            
            # Let's try to mock hasattr at the module level if possible, 
            # but it's easier to just mock os.geteuid and rely on it existing in the mock
            self.assertTrue(is_root())

    def test_is_root_linux_false(self):
        with patch("disk_health_reporter.cli.os") as mock_os:
            mock_os.geteuid.return_value = 1000
            self.assertFalse(is_root())

if __name__ == "__main__":
    unittest.main()
