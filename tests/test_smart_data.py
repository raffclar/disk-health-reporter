import unittest
from unittest.mock import MagicMock, patch

from disk_health_reporter.smart_data import (
    format_smart_data_json,
    format_smart_data_text,
    get_smart_data,
)


class TestSmartData(unittest.TestCase):
    def test_format_smart_data_json(self):
        sample_json = {
            "device": {"name": "/dev/sda", "type": "sat"},
            "model_name": "Test Model",
            "serial_number": "123456",
            "smart_status": {"passed": True},
            "temperature": {"current": 35},
            "ata_smart_attributes": {
                "table": [
                    {
                        "id": 1,
                        "name": "Raw_Read_Error_Rate",
                        "value": 100,
                        "worst": 100,
                        "thresh": 51,
                        "raw": {"string": "0"},
                        "when_failed": ""
                    }
                ]
            }
        }

        formatted = format_smart_data_json(sample_json)

        self.assertEqual(formatted["device"], "/dev/sda")
        self.assertEqual(formatted["model"], "Test Model")
        self.assertEqual(formatted["serial"], "123456")
        self.assertEqual(formatted["overall_health"], True)
        self.assertEqual(formatted["temperature"], 35)
        self.assertEqual(len(formatted["attributes"]), 1)
        self.assertEqual(formatted["attributes"][0]["status"], "OK")

    def test_format_smart_data_text(self):
        sample_text = """
Device Model:     Test Model
Serial Number:    123456
SMART overall-health self-assessment test result: PASSED

=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 16
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  1 Raw_Read_Error_Rate     0x002f   100   100   051    Pre-fail  Always       -       0

"""
        formatted = format_smart_data_text(sample_text)

        self.assertEqual(formatted["model"], "Test Model")
        self.assertEqual(formatted["serial"], "123456")
        self.assertEqual(formatted["overall_health"], True)
        self.assertEqual(len(formatted["attributes"]), 1)
        self.assertEqual(formatted["attributes"][0]["name"], "Raw_Read_Error_Rate")
        self.assertEqual(formatted["attributes"][0]["status"], "OK")

    @patch("disk_health_reporter.smart_data.subprocess.run")
    def test_get_smart_data_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(RuntimeError) as cm:
            get_smart_data("/dev/sda")
        self.assertIn("smartctl not found", str(cm.exception))

    @patch("disk_health_reporter.smart_data.subprocess.run")
    def test_get_smart_data_success(self, mock_run):
        # First call is for version check
        # Second call is for data
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout='{"device": {"name": "/dev/sda"}}')
        ]

        # We need to mock format_smart_data_json to avoid testing it again here
        with patch("disk_health_reporter.smart_data.format_smart_data_json") as mock_format:
            mock_format.return_value = {"device": "/dev/sda"}
            data = get_smart_data("/dev/sda")
            self.assertEqual(data["device"], "/dev/sda")
