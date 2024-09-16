from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import RPi.GPIO as GPIO
import time

# GPIO Mode (BCM)
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for Ultrasonic Sensor
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Function to get distance from the Ultrasonic Sensor
def get_distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Save StartTime and StopTime
    start_time = time.time()
    stop_time = time.time()

    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()

    # Save StopTime
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()

    # Time difference between start and stop
    time_elapsed = stop_time - start_time
    # Multiply with the speed of sound (34300 cm/s) and divide by 2 (for round trip)
    distance = (time_elapsed * 34300) / 2

    return distance

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    # Handle GET requests
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Serve the HTML file
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

        elif self.path == '/data':
            # Get the distance from the Ultrasonic sensor
            distance = get_distance()
            sensor_data = {'distance': distance}

            # Serve the sensor data in JSON format
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(sensor_data).encode('utf-8'))
        else:
            # Handle 404 Not Found
            self.send_response(404)
            self.end_headers()

# Start the server
def run_server():
    server_address = ('', 8000)  # Listen on port 8000
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Starting server on http://localhost:8000...")
    httpd.serve_forever()

# Cleanup GPIO on exit
try:
    run_server()
except KeyboardInterrupt:
    print("Server stopped. Cleaning up GPIO...")
    GPIO.cleanup()