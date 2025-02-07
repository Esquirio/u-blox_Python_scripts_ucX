import asyncio
import json
from gmqtt import Client as MQTTClient
from colorama import init, Fore, Style
import time
import argparse

# Initialize colorama
init(autoreset=True)

# Parse command line arguments
parser = argparse.ArgumentParser(description="MQTT Connection Tester")
parser.add_argument("-b", "--broker_ip", type=str, required=True, help="MQTT broker address")
parser.add_argument("-p", "--port", type=int, required=True, help="MQTT broker port")
parser.add_argument("-fk", "--filter_key", type=str, required=True, help="Filter key for the message")
parser.add_argument("-fv", "--filter_values", type=str, nargs='+', required=True, help="Filter values for the message")
parser.add_argument("-t", "--timeout", type=int, default=20, help="Timeout duration in seconds (default: 20)")
args = parser.parse_args()

# Define the MQTT broker details
broker = args.broker_ip
port = args.port
topic = "angles"
filter_key = args.filter_key
filter_values = set(args.filter_values)  # Use a set for efficient lookups
found_values = set()  # Track found filter values
should_exit = False
message_received = False
timeout_duration = args.timeout

# Define the callback functions
def on_connect(client, flags, rc, properties):
    print(f"{Fore.GREEN}Connected to MQTT Broker!")
    client.subscribe(topic)  # Subscribe to the topic 'angles'

def on_disconnect(client, packet, exc=None):
    print(f"{Fore.YELLOW}Disconnected from MQTT Broker")
    global should_exit
    should_exit = True

def on_message(client, topic, payload, qos, properties):
    global message_received
    try:
        payload = json.loads(payload.decode())
        value = payload.get(filter_key)
        if value in filter_values and value not in found_values:
            print(f"\n{Fore.CYAN}************************************************************")
            print(f"{Fore.GREEN}Message received!")    
            print(f"{Fore.CYAN}Received message from topic {topic}: {payload}")
            print(f"{Fore.CYAN}************************************************************\n")
            found_values.add(value)
            message_received = True
            if found_values == filter_values:
                print(f"{Fore.GREEN}All filter values found: {found_values}. Exiting...")
                asyncio.create_task(client.disconnect())
    except json.JSONDecodeError:
        print(f"{Fore.RED}Failed to decode JSON message")

async def main():
    client = MQTTClient("client_id")

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the MQTT broker
    await client.connect(broker, port)

    start_time = time.time()
    print(f"{Fore.YELLOW}Listening for messages for {timeout_duration} seconds...")

    # Keep the script running to maintain the connection
    try:
        while not should_exit:
            if time.time() - start_time > timeout_duration:
                if not message_received:
                    print(f"{Fore.YELLOW}No messages received based on the filter within the timeout period.")
                break
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}KeyboardInterrupt, exiting...")
    finally:
        if client.is_connected:
            if found_values:
                print(f"{Fore.GREEN}Timeout, exiting ...\nFound values: {found_values}")
            else:
                print(f"{Fore.YELLOW}Timeout, exiting ... No values found")
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
