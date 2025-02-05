import time
from rpi_ws281x import PixelStrip, Color
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configuration for the LED strip
LED_COUNT = 256  # 32x8 matrix, total of 256 LEDs
LED_PIN = 18  # GPIO pin connected to the LED strip (usually GPIO18)
LED_FREQ_HZ = 800000  # LED signal frequency in Hz
LED_DMA = 10  # DMA channel to use for generating signal
LED_BRIGHTNESS = 100  # Brightness level (0-255)
LED_INVERT = False  # True to invert the signal (useful for certain setups)
LED_CHANNEL = 0  # Set to 1 if you're using GPIO 13

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()


def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0)) 
    strip.show()

def get_pixel_index_serpentine(x, y, matrix_width=32, matrix_height=8):
    if x < 0 or x >= matrix_width:
        raise ValueError("x coordinate must be between 0 and {}".format(matrix_width - 1))
    if y < 0 or y >= matrix_height:
        raise ValueError("y coordinate must be between 0 and {}".format(matrix_height - 1))

    if x % 2 == 0:
        pixel_index = x * matrix_height + y
    else:
        pixel_index = x * matrix_height + (matrix_height - 1 - y)
    
    return pixel_index

def coolanim(c):
    clear_strip()
    for x in range(32):
        strip.setPixelColor(get_pixel_index_serpentine(x, 4),c)
        strip.setPixelColor(get_pixel_index_serpentine(x, 3), c)
        strip.show()
        time.sleep(.03)
    for x in range(32):
        strip.setPixelColor(get_pixel_index_serpentine(x, 4), Color(0,0,0))
        strip.setPixelColor(get_pixel_index_serpentine(x, 3), Color(0,0,0))
        strip.show()
        time.sleep(.03)
def is_below_brightness_threshold(r, g, b, threshold):
    # Calculate the luminance of the color
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return luminance < threshold

def display_text(text, c):
    font = ImageFont.load_default()
    image = Image.new('RGB', (32, 8), (0, 0, 0))  # black background
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_position = max(0, (32 - text_width) // 2)  # center text horizontally
    x_position = -1
    y_position = -2  # Move text upwards by 1 pixel to fix the vertical offset
    draw.text((x_position, y_position), text, font=font, fill=(255, 255, 255))
   

    pixels = np.array(image)

    image.save("debug_output.png")
    for y in range(8):
        for x in range(32):
            r, g, b = pixels[y, x]
            color = Color(r, g, b)
            if not (r == 0 and g == 0 and b == 0) and not is_below_brightness_threshold(r, g, b, 50):
                color = c  # Set the color if it's below the threshold
            else:
                color = Color(0, 0, 0)
            strip.setPixelColor(get_pixel_index_serpentine(x, y), color)
    
    strip.show()


def display_weather(text, c):
    font = ImageFont.load_default()
    image = Image.new('RGB', (32, 8), (0, 0, 0))  # black background
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_position = max(0, (32 - text_width) // 2)  # center text horizontally
    x_position = -1
    y_position = -2  # Move text upwards by 1 pixel to fix the vertical offset
    draw.text((x_position, y_position), text, font=font, fill=(255, 255, 255))

    pixels = np.array(image)
    for y in range(8):
        for x in range(32):
            r, g, b = pixels[y, x]
            color = Color(r, g, b)
            if not (r == 0 and g == 0 and b == 0) and not is_below_brightness_threshold(r, g, b, 50):
                color = c  # Set the color if it's below the threshold
            else:
                color = Color(0, 0, 0)
            strip.setPixelColor(get_pixel_index_serpentine(x, y), color)

    strip.show()


def display_text_anim(text, c, up):
    if up:
        for l in range(9, -1,-1):
            font = ImageFont.load_default()
            image = Image.new('RGB', (32, 8), (0, 0, 0))  # black background
            draw = ImageDraw.Draw(image)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = max(0, (32 - text_width) // 2)  
            x_position = -1
            y_position = (-2 + l) 
            draw.text((x_position, y_position), text, font=font, fill=(255, 255, 255))

            pixels = np.array(image)
            for y in range(8):
                for x in range(32):
                    r, g, b = pixels[y, x]
                    color = Color(r, g, b)
                    if not (r == 0 and g == 0 and b == 0) and not is_below_brightness_threshold(r, g, b, 50):
                        color = c  # Set the color if it's below the threshold
                    else:
                        color = Color(0, 0, 0)
                    strip.setPixelColor(get_pixel_index_serpentine(x, y), color)

            strip.show()
            time.sleep(0.05)
    else:
        for l in range(9):
            font = ImageFont.load_default()
            image = Image.new('RGB', (32, 8), (0, 0, 0))  # black background
            draw = ImageDraw.Draw(image)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = max(0, (32 - text_width) // 2)  
            x_position = -1
            y_position = (-2 - l) 
            draw.text((x_position, y_position), text, font=font, fill=(255, 255, 255))

            pixels = np.array(image)
            for y in range(8):
                for x in range(32):
                    r, g, b = pixels[y, x]
                    color = Color(r, g, b)
                    if not (r == 0 and g == 0 and b == 0) and not is_below_brightness_threshold(r, g, b, 50):
                        color = c  # Set the color if it's below the threshold
                    else:
                        color = Color(0, 0, 0)
                    strip.setPixelColor(get_pixel_index_serpentine(x, y), color)

            strip.show()
            time.sleep(0.05)