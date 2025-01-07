# Bluetooth Send Data Script

This script allows you to send data via Bluetooth Classic or Bluetooth Low Energy (BLE) and read the characteristic value after writing for BLE.

## Prerequisites

- Python 3.x
- `pybluez` library for Bluetooth Classic
- `bleak` library for Bluetooth Low Energy (BLE)
- `colorama` library for colored output

## Installation

### Install `pybluez` for Bluetooth Classic

Install `pybluez` using:

```sh
pip install pybluez
```

For Windows 11 OS, run the following command to install the `pybluez` package:

```sh
python -m pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
```

See to the issue [here](https://github.com/pybluez/pybluez/issues/471).

### Install `bleak` for Bluetooth Low Energy (BLE)

Install `bleak` using:

```sh
pip install bleak
```

### Install `colorama` for colored output

Install `colorama` using:

```sh
pip install colorama
```

## Usage

Run the script with the following command:

```sh
python ubx_send_data_bt.py -a <Bluetooth_Address> -t <Connection_Type>
```

### Arguments

- `-a`, `--address`: The target Bluetooth address (required).
- `-t`, `--type`: The type of Bluetooth connection (`classic` or `ble`) (required).

### Example

For Bluetooth Classic:

```sh
python ubx_send_data_bt.py -a 00:1A:7D:DA:71:13 -t classic
```

For Bluetooth Low Energy (BLE):

```sh
python ubx_send_data_bt.py -a 00:1A:7D:DA:71:13 -t ble
```

## Notes

- For BLE, the script will keep the connection open until you stop the script.
- The script will prompt you to enter the number of characters for the data and ask if you want to send more data.
- For Bluetooth Classic, the script will print the sent data in character format.
- For BLE, the script will print the sent and read data in hexadecimal format.