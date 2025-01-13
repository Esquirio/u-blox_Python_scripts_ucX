# My HTTP Server

This project implements a simple HTTP server that serves images from a specified directory.

## Project Structure

```
my-http-server
├── images
│   └── sample.jpg
├── src
│   ├── server.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

Make sure you have Python 3 installed on your machine.

### Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies:

```
pip install -r requirements.txt
```

### Running the Server

Change the variable value:
```
port = 4043  # Sever port
```
To start the HTTP server, run the following command:

```
python src/server.py
```

The server will start and listen for incoming requests.

### Running the Client

Change the variables values:
```
N = 100  # Number of times to run the download process
host_ip_address = "192.168.0.115"  # Host IP address
port = 4043  # Sever port
```

To start the HTTP client, run the following command:

```
python src/server.py
```


### Accessing Images

Once the server is running, you can access the images by navigating to:

```
http://localhost:8000/images/sample.jpg
```

Replace `sample.jpg` with the name of any other image file in the `images` folder to view it.

## License

This project is licensed under the MIT License.
