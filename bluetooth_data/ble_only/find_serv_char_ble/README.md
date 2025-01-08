# UBX Find Service and Characteristic BLE Script

This script scans for BLE devices, connects to a specified device, and lists its services and characteristics. It also attempts to read the value of readable characteristics.

## Prerequisites

- Python 3.7 or higher
- `bleak` library
- `colorama` library

You can install the required libraries using pip:

```sh
pip install bleak colorama
```

## Usage

1. **Set the Device Address:**

   Pass the MAC address of your BLE device as a command-line argument using `-a` or `--address`. The script accepts both formats: `D4:CA:6E:B8:91:85` and `D4CA6EB89185`.

2. **Run the Script:**

   Execute the script using Python:

   ```sh
   python ubx_find_serv_char_ble.py -a <Bluetooth_Address>
   ```

3. **Output:**

   The script will output the services and characteristics of the specified BLE device, including the properties and values of readable characteristics.

## Example

```sh
python ubx_find_serv_char_ble.py -a XX:XX:XX:XX:XX:XX
```

The output will look something like this:

```
Service UUID: 00001800-0000-1000-8000-00805f9b34fb
    Characteristic UUID: 00002a00-0000-1000-8000-00805f9b34fb
        Properties: ['read']
        Value: b'Device Name'
    Characteristic UUID: 00002a01-0000-1000-8000-00805f9b34fb
        Properties: ['read']
        Value: b'\x00\x00'
```

## Error Handling

If the script encounters an error while connecting to the device or reading a characteristic, it will print an error message.

```
Error: Could not connect to device
```

## License

This project is licensed under the MIT License.
