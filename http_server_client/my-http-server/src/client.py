import requests
import time
from datetime import datetime

images_list = ["image_33kb.jpg", "image_53kb.jpg", "image_100kb.jpg", "image_500kb.jpg",
               "image_1mb.jpg", "image_5mb.jpg", "image_10mb.jpg", "image_20mb.jpg",
               "image_105mb.jpg"]

def fetch_image(image_url, save_path, result_file):
    start_time = time.time()
    response = requests.get(image_url)
    end_time = time.time()
    
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f'Image saved to {save_path}')
        
        # Calculate transfer time and throughput
        transfer_time = (end_time - start_time) * 1000  # in milliseconds
        image_size = len(response.content)  # in bytes
        image_size_kb = image_size / 1024  # in kilobytes
        throughput = (image_size) / (end_time - start_time) / (1024 * 1024)  # in Mbps
        
        formatted_start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        
        result = (
            f'***************************************************\n'
            f'Download image {save_path}\n'
            f'Start time: {formatted_start_time}\n'
            f'Transfer time: {transfer_time:.2f} milliseconds\n'
            f'Throughput: {throughput:.2f} Mbps\n'
            f'Received data: {image_size_kb:.2f} kB\n'
            f'***************************************************\n\n'
        )
        
        print(result)
        
        with open(result_file, 'a') as file:
            file.write(result)
    else:
        print(f'Failed to fetch image. Status code: {response.status_code}')

if __name__ == "__main__":
    N = 5  # Number of times to run the download process
    formatted_filename = datetime.now().strftime('%Y.%m.%d.%H.%M.%S_results.txt')
    
    for _ in range(N):
        for image_name in images_list:
            image_url = f'http://localhost:8000/{image_name}'  # URL of the image on the server
            save_path = "sample_received.jpg"
            # save_path = image_name  # Path to save the image
            fetch_image(image_url, save_path, formatted_filename)