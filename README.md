# S.M.A.R.T. Report

A CLI tool that runs smartctl on all block devices, collects S.M.A.R.T. statistics, and emails them as a report with HTML tables.

<img width="532" height="532" alt="image" src="https://github.com/user-attachments/assets/3616ee3f-7eac-4443-bf8e-258c32e38938" />


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
- smartmontools (for the `smartctl` command)
- Superuser access (root on Linux, Administrator on Windows). The tool will check for these privileges upon startup and exit with an error if they are missing.

## Options

- `--email, -e`: Email address to send the report to (required)
- `--from-email, -f`: Email address to send from (defaults to current user@hostname)
- `--smtp-server, -s`: SMTP server to use (defaults to localhost)
- `--smtp-port, -p`: SMTP port to use (defaults to 25)
- `--smtp-user, -u`: SMTP username for authentication
- `--smtp-pass`: SMTP password for authentication
- `--use-tls`: Use TLS for SMTP connection

## Automation

To run this tool every day at midnight, you can use a `cron` job.

1.  Make sure you have installed the tool and its dependencies:
    ```bash
    uv sync
    ```

2.  Ensure `run_daily.sh` is executable:
    ```bash
    chmod +x run_daily.sh
    ```

3.  Open your crontab as root (since `smartctl` requires root permissions):
    ```bash
    sudo crontab -e
    ```

4.  Add the following line to run the script every day at 00:00. Make sure to provide the full path to the project directory and your email address:
    ```bash
    0 0 * * * /path/to/disk-health-reporter/run_daily.sh your-email@example.com
    ```
