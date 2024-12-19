from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import socket
from colorama import Fore, Style, init

ip_address = "192.168.0.115"
port = 4043

class ImageRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip, client_port = self.client_address
        print(f'{Fore.BLUE}Received request from {client_ip}:{client_port}')
        if self.path.startswith('/images/'):
            self.path = self.path[1:]  # Remove leading '/'
        return super().do_GET()

init(autoreset=True)

def run(server_class=HTTPServer, handler_class=ImageRequestHandler, port=4043):
    script_dir = os.path.dirname(__file__)  # Get the directory of the script
    images_dir = os.path.join(script_dir, '..', 'images')  # Construct the full path to the images directory
    os.chdir(images_dir)  # Change directory to images folder
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    # Get the server IP address
    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)
    
    print(f'{Fore.GREEN}Serving on IP {ip_address} and port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()