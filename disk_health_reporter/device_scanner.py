import os
import subprocess
from typing import List


def get_block_devices() -> List[str]:
    """
    Get a list of block devices on the system.

    Returns:
        list: List of block device paths (e.g., /dev/sda, /dev/nvme0n1)

    Raises:
        RuntimeError: If no block devices found
        RuntimeError: If lsb fails
        RuntimeError: If /dev cannot be found
    """
    devices = []

    if os.path.exists("/dev"):
        result = subprocess.run(
            ["lsblk", "-d", "-o", "NAME", "-n"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list block devices: {result.stderr}")
        block_devices = result.stdout.strip().split("\n")

        if len(block_devices) == 0:
            raise RuntimeError("No block devices found")

        for line in block_devices:
            if line:
                device_name = line.strip()
                # Skip loop, ram, and other non-physical devices
                if not any(
                    device_name.startswith(prefix) for prefix in ["loop", "ram"]
                ):
                    devices.append(f"/dev/{device_name}")
        return devices
    else:
        raise RuntimeError("The /dev directory does not exist")
