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

To start the HTTP server, run the following command:

```
python src/server.py
```

The server will start and listen for incoming requests.

### Accessing Images

Once the server is running, you can access the images by navigating to:

```
http://localhost:8000/images/sample.jpg
```

Replace `sample.jpg` with the name of any other image file in the `images` folder to view it.

## License

This project is licensed under the MIT License.