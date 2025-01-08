# Bluetooth GATT Read/Write Script

This script allows you to read from and write to a Bluetooth device's GATT characteristics.

## Prerequisites

- Python 3.7 or higher
- `bleak` library
- `colorama` library

## Usage

To run the script, use the following command:

```sh
python ubx_write_and_read_char_blet.py -a <MAC_ADDRESS>
```

### Arguments

- `-a`, `--address`: The MAC address of the Bluetooth device.

### Example

```sh
python ubx_write_and_read_char_ble.py -a XX:XX:XX:XX:XX:XX
```
or 
```sh
python ubx_write_and_read_char_ble.py -a XXXXXXXXXXXX
```

## Description

The script performs the following actions:

1. Connects to the u-blox Bluetooth device with the specified MAC address.
2. Writes a byte value (`0x00`) to a characteristic.
3. Reads the value from the characteristic and prints it.
4. Writes another byte value (`0x23`) to the characteristic.
5. Reads the value from the characteristic and prints it.

## Notes

- Ensure that the Bluetooth device is powered on and within range.