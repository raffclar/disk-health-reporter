import getpass
import smtplib
import socket
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import jinja2


def send_email_report(
    smart_data,
    to_email,
    from_email=None,
    smtp_server="localhost",
    smtp_port=25,
    smtp_user=None,
    smtp_pass=None,
    use_tls=False,
):
    """
    Send S.M.A.R.T. data report via email.

    Args:
        smart_data (dict): Dictionary of device paths and their S.M.A.R.T. data
        to_email (str): Email address to send the report to
        from_email (str, optional): Email address to send from (defaults to current user@hostname)
        smtp_server (str, optional): SMTP server to use. Defaults to "localhost".
        smtp_port (int, optional): SMTP port to use. Defaults to 25.
        smtp_user (str, optional): SMTP username for authentication
        smtp_pass (str, optional): SMTP password for authentication
        use_tls (bool, optional): Whether to use TLS encryption. Defaults to False.
    """
    if not from_email:
        user = getpass.getuser()
        host = socket.gethostname()
        from_email = f"{user}@{host}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"S.M.A.R.T. Report for {socket.gethostname()} - "
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}'
    )
    msg["From"] = from_email
    msg["To"] = to_email

    html_content = generate_html_report(smart_data)
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        if use_tls:
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def generate_html_report(smart_data):
    """
    Generate HTML report from S.M.A.R.T. data.

    Args:
        smart_data (dict): Dictionary of device paths and their S.M.A.R.T. data

    Returns:
        str: HTML content of the report
    """
    template_path = Path(__file__).parent
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    template = env.get_template("report.jinja2")
    html_content = template.render(
        devices=smart_data,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hostname=socket.gethostname(),
    )
    return html_content
