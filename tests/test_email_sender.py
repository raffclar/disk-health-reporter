import unittest
from unittest.mock import MagicMock, patch

from disk_health_reporter.email_sender import generate_html_report, send_email_report


class TestEmailSender(unittest.TestCase):
    def setUp(self):
        self.smart_data = {
            "/dev/sda": {
                "device": "/dev/sda",
                "model": "Test Model",
                "serial": "123456",
                "type": "sat",
                "overall_health": True,
                "temperature": 35,
                "attributes": [
                    {
                        "id": "1",
                        "name": "Raw_Read_Error_Rate",
                        "value": "100",
                        "worst": "100",
                        "threshold": "51",
                        "raw_value": "0",
                        "status": "OK"
                    }
                ]
            }
        }

    @patch("disk_health_reporter.email_sender.smtplib.SMTP")
    @patch("disk_health_reporter.email_sender.socket.gethostname")
    @patch("disk_health_reporter.email_sender.getpass.getuser")
    @patch("disk_health_reporter.email_sender.generate_html_report")
    def test_send_email_report_defaults(self, mock_gen_report, mock_getuser, mock_gethostname, mock_smtp):
        mock_getuser.return_value = "testuser"
        mock_gethostname.return_value = "testhost"
        mock_gen_report.return_value = "<html>Test Report</html>"

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_email_report(self.smart_data, "recipient@example.com")

        # Verify SMTP connection
        mock_smtp.assert_called_once_with("localhost", 25)

        # Verify email construction
        args, kwargs = mock_server.send_message.call_args
        msg = args[0]
        self.assertEqual(msg["To"], "recipient@example.com")
        self.assertEqual(msg["From"], "testuser@testhost")
        self.assertIn("S.M.A.R.T. Report for testhost", msg["Subject"])

        # Verify content
        self.assertEqual(msg.get_payload()[0].get_payload(), "<html>Test Report</html>")

    @patch("disk_health_reporter.email_sender.smtplib.SMTP")
    def test_send_email_report_custom_smtp(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_email_report(
            self.smart_data,
            "recipient@example.com",
            from_email="sender@example.com",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            smtp_user="user",
            smtp_pass="pass",
            use_tls=True
        )

        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.send_message.assert_called_once()

    @patch("disk_health_reporter.email_sender.jinja2.Environment")
    @patch("disk_health_reporter.email_sender.socket.gethostname")
    def test_generate_html_report(self, mock_gethostname, mock_jinja_env):
        mock_gethostname.return_value = "testhost"
        mock_template = MagicMock()
        mock_jinja_env.return_value.get_template.return_value = mock_template

        generate_html_report(self.smart_data)

        mock_template.render.assert_called_once()
        args, kwargs = mock_template.render.call_args
        self.assertEqual(kwargs["devices"], self.smart_data)
        self.assertEqual(kwargs["hostname"], "testhost")
