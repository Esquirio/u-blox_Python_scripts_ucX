# MQTT Connection Tester

This script is designed to test MQTT connections and filter messages based on specified criteria. It can be helpful to find the Anchor ID for u-locate system installations.

## Features

- Connects to an MQTT broker
- Subscribes to a specified topic
- Filters messages based on a specified key and list of values
- Prints received messages that match the filter criteria
- Exits when all filter values are found or after a specified timeout

## Requirements

The script requires the following Python modules:

- `gmqtt`
- `colorama`
- `argparse`

You can install these modules using pip:

```sh
pip install gmqtt colorama argparse
```

## Usage

To run the script, use the following command:

```sh
python mqtt_tester.py -b <broker_ip> -p <port> -fk <filter_key> -fv <filter_value1> <filter_value2> ... -t <timeout>
```

### Parameters

- `-b`, `--broker_ip`: The IP address of the MQTT broker (required)
- `-p`, `--port`: The port of the MQTT broker (required)
- `-fk`, `--filter_key`: The key to filter messages by (required)
- `-fv`, `--filter_values`: The values to filter messages by (required, can be multiple values)
- `-t`, `--timeout`: The timeout duration in seconds (optional, default is 20 seconds)

### Example

```sh
python mqtt_tester.py -b 10.12.71.47 -p 1883 -fk anchor_name -fv AP01 AP02 AP03 -t 30
```

This command will connect to the MQTT broker at `10.12.71.47` on port `1883`, subscribe to the topic `angles`, and filter messages based on the key `anchor_name` with values `AP01`, `AP02` and `AP03`. The script will run for 30 seconds or until all filter values are found.

This command will connect to the MQTT broker at `10.12.71.47` on port `1883`, subscribe to the topic `angles`, and filter messages based on the key `anchor_id` with values `54F82A53C7E1` and `54F82A53C7E2`. The script will run for 30 seconds or until all filter values are found.

## License

This project is licensed under the MIT License.