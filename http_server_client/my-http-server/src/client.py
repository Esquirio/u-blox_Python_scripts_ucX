import requests
import time
from datetime import datetime

images = ["image_33kb.jpg", "image_53kb.jpg", "image_100kb.jpg", "image_500kb.jpg",
            "image_1mb.jpg", "image_5mb.jpg", "image_10mb.jpg", "image_20mb.jpg",
            "image_105mb.jpg"]

image_name = images[0]  # Replace with the name of the image you want to fetch

def fetch_image(image_url, save_path):
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
        throughput = (image_size * 8) / (end_time - start_time) / (1024 * 1024)  # in Mbps
        
        formatted_start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f'Start time: {formatted_start_time}')
        print(f'Transfer time: {transfer_time:.2f} milliseconds')
        print(f'Throughput: {throughput:.2f} Mbps')
        print(f'Received data: {image_size_kb:.2f} kB')
    else:
        print(f'Failed to fetch image. Status code: {response.status_code}')

if __name__ == "__main__":
    image_url = f'http://localhost:8000/{image_name}'  # URL of the image on the server
    save_path = 'sample_received.jpg'  # Path to save the image
    fetch_image(image_url, save_path)