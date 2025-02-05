import threading
import time
from rpi_ws281x import Color
import newmatrix
import pytz
import weather
from datetime import datetime
from flask import Flask, request, jsonify
import random
from flask import render_template_string

# Constants and variables
MODE = 0
switchTime = 13  # Duration for displaying the time
api_key = 'fdcfe1b9c1a5239a306222c9e50388d4'
easetime = 0.0001
brightness = 0.4

# Flask app
app = Flask(__name__)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LED Matrix Control</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
        .slider-container { margin: 20px; }
        label { display: block; margin-bottom: 5px; }
        input[type="range"] { width: 300px; }
        span.slider-value { font-weight: bold; margin-left: 10px; }
    </style>
</head>
<body>
    <h1>LED Matrix Control</h1>
    <div class="slider-container">
        <label for="brightness">Brightness: 
            <span id="brightness-value" class="slider-value">{{ brightness }}</span>
        </label>
        <input 
            type="range" 
            id="brightness" 
            min="0" 
            max="0.8" 
            step="0.1" 
            value="{{ brightness }}" 
            oninput="document.getElementById('brightness-value').textContent = this.value">
    </div>
    <div class="slider-container">
        <label for="switchTime">Switch Time (seconds): 
            <span id="switchTime-value" class="slider-value">{{ switchTime }}</span>
        </label>
        <input 
            type="range" 
            id="switchTime" 
            min="1" 
            max="30" 
            step="1" 
            value="{{ switchTime }}" 
            oninput="document.getElementById('switchTime-value').textContent = this.value">
    </div>
    <button onclick="updateValues()">Update</button>
    <p id="status"></p>
    <script>
        function updateValues() {
            const brightness = parseFloat(document.getElementById('brightness').value);
            const switchTime = parseInt(document.getElementById('switchTime').value, 10);
            
            fetch('/update_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ brightness, switchTime })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.message;
                document.getElementById('brightness-value').textContent = brightness.toFixed(1);
                document.getElementById('switchTime-value').textContent = switchTime;
            })
            .catch(err => {
                document.getElementById('status').textContent = 'Error updating settings.';
                console.error(err);
            });
        }
    </script>
</body>
</html>
"""

def get_mode():
    """Returns the current mode."""
    return MODE

def multiply_color(color, factor):
    """Multiplies the color by a given factor (scaling its RGB components)."""
    red = min(int(color.r * factor), 255)  # Ensure the value is <= 255
    green = min(int(color.g * factor), 255)
    blue = min(int(color.b * factor), 255)
    return Color(red, green, blue)

def display_time(color):
    now = datetime.now()
    hour = now.hour
    minute = now.minute - 10
    if hour < 0:
        hour = 23  # Wrap around to 23 if we go below 0

    adjusted_hour = hour if now.hour != 0 else now.hour
    current_time = now.replace(hour=adjusted_hour, minute=now.minute, second=now.second).strftime(' %H : %M')
    print(current_time)
    time_display = current_time

    newmatrix.display_text_anim(time_display, color, True)

    start_time = time.time()
    while time.time() - start_time < switchTime:
        if get_mode() != 0:
            print("Mode changed, exiting display_time.")
            return

        now = datetime.now()
        hour = now.hour
        if hour < 0:
            hour = 23

        adjusted_hour = hour if now.hour != 0 else now.hour
        current_time = now.replace(hour=adjusted_hour, minute=now.minute, second=now.second).strftime(' %H : %M')

        for i in range(2):
            if get_mode() != 0:
                print("Mode changed during blink, exiting display_time.")
                return
            time_display = current_time if i == 0 else current_time.replace(':', ' ')
            print(time_display)
            newmatrix.display_text(time_display, color)
            time.sleep(0.5)

    newmatrix.display_text_anim(time_display, color, False)

def display_date(color):
    current_date = datetime.now()
    formatted_date = "  " + current_date.strftime("%d.%m")
    newmatrix.display_text_anim(formatted_date, color, True)
    newmatrix.display_text(formatted_date, color)
    time.sleep(switchTime)
    newmatrix.display_text_anim(formatted_date, color, False)

def display_weather(color):
    currentTemp = weather.get_weather("Spardorf", api_key)
    print(currentTemp[0])
    

    time_display = "   " + str(int(currentTemp[0])) + " ° C"
    if currentTemp[0] > 9:
        time_display = " " + str(int(currentTemp[0])) + " ° C"
    newmatrix.display_text_anim(time_display, color, True)
    newmatrix.display_text(time_display, color)
    time.sleep(switchTime)
    newmatrix.display_text_anim(time_display, color, False)

def get_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return multiply_color(Color(red, green, blue), brightness)

def switch_mode():
    while True:
        randomColor = get_random_color()
        display_time(randomColor)
        randomColor = get_random_color()
        display_date(randomColor)
        randomColor = get_random_color()
        display_weather(randomColor)

@app.route('/')
def control_page():
    """Renders the control page."""
    return render_template_string(HTML_TEMPLATE, brightness=brightness, switchTime=switchTime)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Updates brightness and switchTime settings."""
    global brightness, switchTime
    data = request.json
    brightness = data.get('brightness', brightness)
    switchTime = data.get('switchTime', switchTime)
    return jsonify({"status": "success", "message": "Settings updated successfully!"})

# Start the Flask app in a separate thread
def run_webserver():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the web server in a separate thread
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.daemon = True
    webserver_thread.start()

    # Start the display logic
    switch_mode()
