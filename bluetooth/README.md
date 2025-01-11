# Bluetooth Send Data Script

This script allows you to send data via Bluetooth Classic or Bluetooth Low Energy (BLE) and read the characteristic value after writing for BLE.

For BLE, it is possible to send data using the u-blox Serial Port Service (SPS) or send data to a user-defined service and characteristic.

## Prerequisites

- Python 3.x
- `pybluez` library for Bluetooth Classic
- `bleak` library for Bluetooth Low Energy (BLE)
- `colorama` library for colored output

## Installation

Install the required libraries using pip:

```sh
pip install bleak pybluez colorama
```

For Windows 11 OS, run the following command to install the `pybluez` package:

```sh
python -m pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
```

See to the issue [here](https://github.com/pybluez/pybluez/issues/471).

## Usage

Run the script with the following command-line arguments:

```sh
python ubx_send_data_bt.py -a <TARGET_ADDRESS> -t <TYPE> --data_size <MAX_DATA_SIZE> --xtimes <XTIMES>
```

### Arguments

- `-a`, `--address`: The target Bluetooth address (required).
- `-t`, `--type`: The type of Bluetooth connection (`classic` or `ble`) (required).
- `--data_size`: The maximum number of characters to send (required). The script will send data starting from 1 byte up to the specified maximum size.
- `--xtimes`: The number of times the script should run for each data size (required). If set to 0, the script will send the maximum data size once.
- `--debug`: Enable debug messages

Change the `service_uuid` and `characteristic_uuid` for the one that was configured on the u-blox module.
For the service and characteristic defined in the u-blox Serial Port Service (SPS), use:
```
service_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d701"
characteristic_uuid = "2456e1b9-26e2-8f83-e744-f34f01e9d703"
```
> [!NOTE]
> For more information about the u-blox Serial Port Service (SPS), refer to the [u-blox documentation](https://u-blox.com/docs/UBX-16011192).

### Example

Sending data via Bluetooth Classic to a target device with address `00:1A:7D:DA:71:13`, with a maximum data size of 5000 bytes, running the script 1 time for each data size:

```sh
python ubx_send_data_bt.py -a 00:1A:7D:DA:71:13 -t classic --data_size 5000 --xtimes 1
```

Sending data via BLE to a target device with address `00:1A:7D:DA:71:13`, with a maximum data size of 10 bytes, running the script 5 times for each data size and enabling the debug messages:

```sh
python ubx_send_data_bt.py -a 00:1A:7D:DA:71:13 -t ble --data_size 10 --xtimes 5 --debug
```

Sending the 2000 bytes via Bluetooth Classic once:

```sh
python ubx_send_data_bt.py -a 00:1A:7D:DA:71:13 -t classic --data_size 10 --xtimes 0
```

## Notes

- The script limits the data length to 244 bytes for customized services and characteristics as per u-blox documentation.
- For pre-configured services and characteristics starting with "2456e1b9", the script allows sending up to 4148 bytes.
- The script will keep the connection open until you stop the script.
- For Bluetooth Classic and BLE SPS, the script will print the sent data in character format.
- For BLE, the script will print the sent and read data in hexadecimal format.

## License

This project is licensed under the MIT License.