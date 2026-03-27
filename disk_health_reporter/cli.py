#!/usr/bin/env python3

import argparse
import os
import sys

from rich.console import Console
from rich.panel import Panel

from disk_health_reporter.device_scanner import get_block_devices
from disk_health_reporter.email_sender import send_email_report
from disk_health_reporter.smart_data import get_smart_data

console = Console()


def is_root():
    """Check if the current user has superuser privileges."""
    if hasattr(os, "geteuid"):
        return os.geteuid() == 0
    # Fallback for Windows or other systems where geteuid is not available
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, ImportError):
        return False


def main():
    """
    Collect S.M.A.R.T. data from all block devices and email a report.

    This tool scans your system for block devices, runs smartctl on each one,
    and sends the collected data as an HTML report to the specified email address.
    """
    parser = argparse.ArgumentParser(
        description="""Collect S.M.A.R.T. data from all block devices and email a report.
        This tool scans your system for block devices, runs smartctl on each one,
        and sends the collected data as an HTML report to the specified email address."""
    )

    parser.add_argument(
        "--email", "-e", required=True,
        help="Email address to send the report to."
    )
    parser.add_argument(
        "--from-email", "-f",
        help="Email address to send the report from (defaults to system user)."
    )
    parser.add_argument(
        "--smtp-server", "-s", default="localhost",
        help="SMTP server to use for sending email."
    )
    parser.add_argument(
        "--smtp-port", "-p", default=25, type=int,
        help="SMTP port to use for sending email."
    )
    parser.add_argument(
        "--smtp-user", "-u",
        help="SMTP username for authentication (if required)."
    )
    parser.add_argument(
        "--smtp-pass",
        help="SMTP password for authentication (if required)."
    )
    parser.add_argument(
        "--use-tls", action="store_true",
        help="Use TLS for SMTP connection."
    )

    args = parser.parse_args()

    if not is_root():
        console.print("[bold red]Error: This tool requires superuser (root/administrator) privileges to run smartctl.[/bold red]")
        return 1

    try:
        console.print(
            Panel.fit("🔍 Scanning for block devices...", title="S.M.A.R.T. Report")
        )

        # Get list of block devices
        devices = get_block_devices()
        if not devices:
            console.print("[bold red]No block devices found![/bold red]")
            return 1

        console.print(f"Found [bold green]{len(devices)}[/bold green] block devices")

        # Collect SMART data for each device
        console.print("\n[bold]Collecting S.M.A.R.T. data...[/bold]")
        smart_data = {}

        for device in devices:
            try:
                console.print(f"Processing [cyan]{device}[/cyan]...")
                smart_data[device] = get_smart_data(device)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to get S.M.A.R.T. "
                    f"data for {device}: {e}[/yellow]"
                )

        if not smart_data:
            console.print(
                "[bold red]Failed to "
                "collect S.M.A.R.T. data from any device![/bold red]"
            )
            return 1

        # Send email report
        console.print("\n[bold]Sending email report...[/bold]")
        send_email_report(
            smart_data=smart_data,
            to_email=args.email,
            from_email=args.from_email,
            smtp_server=args.smtp_server,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_pass=args.smtp_pass,
            use_tls=args.use_tls,
        )

        console.print("[bold green]✓ Report sent successfully![/bold green]")
        return 0

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
