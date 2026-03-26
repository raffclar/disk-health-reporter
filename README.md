# S.M.A.R.T. Report

A CLI tool that runs smartctl on all block devices, collects S.M.A.R.T. statistics, and emails them as a report with HTML tables.

## Installation

This package uses `uv` for dependency management. To install:

```bash
# Install the package and dependencies
uv sync
```

## Usage

```bash
# Basic usage
uv run disk-health-reporter --email admin@example.com

# Using a specific SMTP server with authentication
uv run disk-health-reporter --email admin@example.com --smtp-server smtp.example.com --smtp-port 587 --smtp-user username --smtp-pass password --use-tls
```

## Requirements

- Python 3.10+
- smartmontools (for the smartctl command)
- superuser access (to run smartctl)

## Options

- `--email, -e`: Email address to send the report to (required)
- `--from-email, -f`: Email address to send from (defaults to current user@hostname)
- `--smtp-server, -s`: SMTP server to use (defaults to localhost)
- `--smtp-port, -p`: SMTP port to use (defaults to 25)
- `--smtp-user, -u`: SMTP username for authentication
- `--smtp-pass`: SMTP password for authentication
- `--use-tls`: Use TLS for SMTP connection
