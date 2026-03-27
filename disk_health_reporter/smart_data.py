import json
import re
import subprocess


def get_smart_data(device_path):
    """
    Get S.M.A.R.T. data for a specific device using smartctl.

    Args:
        device_path (str): Path to the block device (e.g., /dev/sda)

    Returns:
        dict: Parsed S.M.A.R.T. data for the device

    Raises:
        RuntimeError: If smartctl fails or returns an error
    """
    # Check if smartctl is available
    try:
        subprocess.run(["smartctl", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        raise RuntimeError("smartctl not found. Please install the smartmontools package.")

    try:
        # Try to get data in JSON format
        result = subprocess.run(
            ["smartctl", "-a", "-j", device_path], capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            if "Permission denied" in result.stderr or "Operation not permitted" in result.stderr:
                raise RuntimeError(f"Permission denied running smartctl on {device_path}. Make sure you are running as root.")
            raise RuntimeError(f"smartctl returned non-zero exit code: {result.stderr.strip()}")
        data = json.loads(result.stdout)
        return format_smart_data_json(data)
    except subprocess.SubprocessError as error:
        raise RuntimeError(f"Failed to run smartctl on {device_path}") from error


def format_smart_data_json(data):
    """
    Format the JSON S.M.A.R.T. data into a standardized structure.

    Args:
        data (dict): JSON data from smartctl

    Returns:
        dict: Formatted S.M.A.R.T. data
    """
    formatted_data = {
        "device": data.get("device", {}).get("name", "Unknown"),
        "model": data.get("model_name", "Unknown"),
        "serial": data.get("serial_number", "Unknown"),
        "type": data.get("device", {}).get("type", "Unknown"),
        "overall_health": data.get("smart_status", {}).get("passed", "Unknown"),
        "temperature": None,
        "attributes": [],
    }

    # Get temperature
    if "temperature" in data:
        formatted_data["temperature"] = data["temperature"].get("current", None)

    # Get SMART attributes
    if "ata_smart_attributes" in data and "table" in data["ata_smart_attributes"]:
        for attr in data["ata_smart_attributes"]["table"]:
            formatted_data["attributes"].append(
                {
                    "id": attr.get("id", ""),
                    "name": attr.get("name", "Unknown"),
                    "value": attr.get("value", ""),
                    "worst": attr.get("worst", ""),
                    "threshold": attr.get("thresh", ""),
                    "raw_value": attr.get("raw", {}).get("string", ""),
                    "status": "OK" if attr.get("when_failed", "") == "" else "FAILING",
                }
            )

    return formatted_data


def format_smart_data_text(text_output):
    """
    Parse the text output from smartctl into a standardized structure.

    Args:
        text_output (str): Text output from smartctl -a

    Returns:
        dict: Formatted S.M.A.R.T. data
    """
    formatted_data = {
        "device": "Unknown",
        "model": "Unknown",
        "serial": "Unknown",
        "type": "Unknown",
        "overall_health": "Unknown",
        "temperature": None,
        "attributes": [],
    }

    # Parse device info
    model_match = re.search(r"Device Model:\s+(.+)", text_output)
    if model_match:
        formatted_data["model"] = model_match.group(1).strip()

    serial_match = re.search(r"Serial Number:\s+(.+)", text_output)
    if serial_match:
        formatted_data["serial"] = serial_match.group(1).strip()

    # Parse overall health
    health_match = re.search(
        r"SMART overall-health self-assessment test result: (.+)", text_output
    )
    if health_match:
        health_status = health_match.group(1).strip()
        formatted_data["overall_health"] = health_status == "PASSED"

    # Parse temperature
    temp_match = re.search(r"Temperature:\s+(\d+)", text_output)
    if temp_match:
        formatted_data["temperature"] = int(temp_match.group(1))

    # Parse attributes
    attr_section = re.search(
        r"SMART Attributes Data Structure.+?ID#.+?\n(.+?)(?:\n\n|\Z)",
        text_output,
        re.DOTALL,
    )

    if attr_section:
        for line in attr_section.group(1).strip().split("\n"):
            parts = re.split(r"\s+", line.strip())
            if len(parts) >= 10:
                attr_id = parts[0]
                attr_name = parts[1]
                attr_value = parts[3]
                attr_worst = parts[4]
                attr_thresh = parts[5]
                attr_raw = parts[9]

                formatted_data["attributes"].append(
                    {
                        "id": attr_id,
                        "name": attr_name,
                        "value": attr_value,
                        "worst": attr_worst,
                        "threshold": attr_thresh,
                        "raw_value": attr_raw,
                        "status": (
                            "OK"
                            if int(attr_value) > int(attr_thresh)
                            else "FAILING" if attr_thresh != "000" else "OK"
                        ),
                    }
                )

    return formatted_data
