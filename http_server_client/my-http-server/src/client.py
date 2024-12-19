import requests
import time
from datetime import datetime
import os
from colorama import Fore, Style, init

N = 100  # Number of times to run the download process
host_ip_address = "192.168.0.115"
port = 4043

# Used power mode during the test
power_mode_config = "AT+UWCFG=1,0" # 0: Wi-Fi ACTIVE mode
                                   # 1: Wi-Fi STANDBY mode
                                   # 2 (default): Wi-Fi SLEEP mode

images_list = ["image_33kb.jpg", "image_53kb.jpg", "image_100kb.jpg", "image_500kb.jpg",
               "image_1mb.jpg", "image_5mb.jpg", "image_10mb.jpg", "image_20mb.jpg"]

init(autoreset=True)

def fetch_image(image_url, image_name, result_file):
  # Ensure the results directory exists
  results_dir = 'results'
  if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    
  # Ensure the rec_images directory exists
  rec_images_dir = 'rec_images'
  if not os.path.exists(rec_images_dir):
    os.makedirs(rec_images_dir)
    
  # Update the result file path to include the results directory
  result_file_path = os.path.join(results_dir, result_file)
  
  # Update the image file path to include the rec_images directory
  image_file_path = os.path.join(rec_images_dir, image_name)
  
  # Get the start time
  start_time = time.time()
  formatted_start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S:%f')
  print(f'{Fore.GREEN}Start time:\t{formatted_start_time}')

  # Fetch the image
  response = requests.get(image_url)

  # Get the end time
  end_time = time.time()
    
  if response.status_code == 200:
    with open(image_file_path, 'wb') as file:
        file.write(response.content)
    # print(f'Image saved to {image_file_path}') # For debug
    
    # Calculate transfer time and throughput
    transfer_time = (end_time - start_time) * 1000  # in milliseconds
    image_size = len(response.content)  # in bytes
    image_size_kb = image_size / 1024  # in kilobytes
    throughput = (image_size * 8) / (end_time - start_time) / (1024 * 1024)  # in Mbps
    
    result = (
        f'***************************************************\n'
        f'NINA Power mode configuration: {power_mode_config}\n'
        f'Download image {image_name}\n'
        f'Start time: {formatted_start_time}\n'
        f'Transfer time: {transfer_time:.2f} milliseconds\n'
        f'Throughput: {throughput:.2f} Mbps\n'
        f'Received data: {image_size_kb:.2f} kB\n'
        f'***************************************************\n\n'
    )
    
    # print(result)  # For debug
    
    with open(result_file_path, 'a') as file:
        file.write(result)
  else:
    print(f'{Fore.RED}Failed to fetch image. Status code: {response.status_code}')

if __name__ == "__main__":  
  for image_name in images_list:  
    filename = datetime.now().strftime('%Y.%m.%d.%H.%M.%S_results.txt')
    print(f'{Fore.YELLOW}-----------------------------------------------------------')
    for i in range(N):
      print(f'{Fore.BLUE}{i+1}-Fetching image: {image_name}')
      image_url = f'http://{host_ip_address}:{port}/{image_name}'  # URL of the image on the server
      fetch_image(image_url, image_name, filename)
    
  print(f'{Fore.YELLOW}-----------------------------------------------------------\n')