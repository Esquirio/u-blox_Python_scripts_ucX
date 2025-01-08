# Bluetooth Send Data Script (BLE)

This script allows you to send data via Bluetooth Low Energy (BLE) and read the characteristic value after writing using the u-blox Serial Port Service (SPS).

## Documentation

For more information, refer to the [u-blox documentation](https://u-blox.com/docs/UBX-16011192).

## Prerequisites

- Python 3.x
- `bleak` library for Bluetooth Low Energy (BLE)
- `colorama` library for colored output

## Installation

### Install `bleak` for Bluetooth Low Energy (BLE)

```sh
pip install bleak
```

### Install `colorama` for colored output

```sh
pip install colorama
```

## Usage

Run the script with the following command:

```sh
python ubx_send_data_ble.py -a <Bluetooth_Address>
```

### Arguments

- `-a`, `--address`: The target Bluetooth address (required).

### Example

```sh
python ubx_send_data_ble.py -a 00:1A:7D:DA:71:13
```

## Notes

- The script will keep the BLE connection open until you stop the script.
- The script will prompt you to enter the number of characters for the data and ask if you want to send more data.
- The script will print the sent and read data in hexadecimal format.
