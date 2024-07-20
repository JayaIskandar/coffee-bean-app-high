import streamlit as st
import random
import json
import os

# Define base directory where the JSON file is located
base_dir = os.path.abspath(os.path.dirname(__file__))
json_path = os.path.join(base_dir, 'coffee_drinks.json')
css_path = os.path.join(base_dir, 'style.css')
js_path = os.path.join(base_dir, 'wheel-script.js')

# Function to read file contents
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to read JSON data
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to create the spinning wheel HTML
def spin_the_wheel():
    # Read JSON data
    coffee_drinks = read_json(json_path)
    drinks = json.dumps([drink['name'] for drink in coffee_drinks])
    descriptions = json.dumps([drink['description'] for drink in coffee_drinks])
    images = json.dumps([drink['image'] for drink in coffee_drinks])

    # Read CSS and JS files
    css_content = read_file(css_path)
    js_content = read_file(js_path)

    return f"""
    <style>
    {css_content}
    </style>
    <div class="wheel-container">
        <canvas id="wheel" width="600" height="600"></canvas>
        <button id="spin-wheel-button" onclick="spinWheel()">Spin the Wheel!</button>
        <h2 id="result"></h2>
    </div>
    <script>
        const drinks = {drinks};
        const descriptions = {descriptions};
        const images = {images};
        {js_content}
    </script>
    """


# Streamlit UI
def show_coffee_wheel_page():
    st.title("Spin the Coffee Wheel!")
    st.write("Don't know what coffee to drink for your day? Try this wheel!")
    st.write("Click the button to spin the wheel and get a random coffee drink.")
    st.components.v1.html(spin_the_wheel(), height=700)

if __name__ == "__main__":
    show_coffee_wheel_page()
