import streamlit as st
import random
import json
import os

# List of coffee drinks and their descriptions
coffee_drinks = [
    ("Iced Mocha", "A chocolatey iced coffee drink made with espresso, milk, and chocolate syrup. Beans: Arabica"),
    ("Cold Brew Coffee", "Coffee brewed with cold water for a smooth flavor. Beans: Robusta"),
    ("Affogato", "A scoop of vanilla ice cream topped with a shot of hot espresso. Beans: Arabica"),
    ("Espresso con Panna", "Espresso topped with whipped cream. Beans: Arabica"),
    ("Frappé", "A Greek iced coffee drink made with instant coffee, sugar, and water. Beans: Robusta"),
    ("Espresso Macchiato", "Espresso with a small amount of steamed milk. Beans: Arabica"),
    ("Ristretto", "A short shot of espresso, stronger in flavor. Beans: Arabica"),
    ("Double Espresso", "Two shots of espresso for a bolder flavor. Beans: Arabica"),
    ("Lungo", "A longer shot of espresso, with more water. Beans: Arabica"),
    ("Iced Latte", "Cold milk and espresso over ice. Beans: Arabica"),
    ("Freakshake", "An indulgent milkshake topped with sweets and often espresso. Beans: Arabica"),
    ("Latte Macchiato", "Steamed milk with a shot of espresso. Beans: Arabica"),
    ("Caffè Mocha", "A latte with chocolate syrup, topped with whipped cream. Beans: Arabica"),
    ("Espresso", "A concentrated coffee brewed by forcing hot water through finely-ground coffee. Beans: Arabica"),
    ("Cafè au Lait", "Coffee with steamed milk. Beans: Arabica"),
    ("Cappuccino", "Equal parts espresso, steamed milk, and milk foam. Beans: Arabica"),
    ("Flat White", "A latte with a higher ratio of coffee to milk. Beans: Arabica"),
    ("Caffè Latte", "Espresso with steamed milk. Beans: Arabica"),
    ("Irish Coffee", "Coffee with Irish whiskey and cream. Beans: Arabica"),
    ("Americano", "Espresso diluted with hot water. Beans: Arabica")
]

# Define base directory where the JSON file is located
base_dir = os.path.abspath(os.path.dirname(__file__))
css_path = os.path.join(base_dir, 'style.css')
js_path = os.path.join(base_dir, 'wheel-script.js')

# Function to read file contents
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to create the spinning wheel HTML
def spin_the_wheel():
    # Pre-process the coffee_drinks list
    drinks = json.dumps([drink[0] for drink in coffee_drinks])
    descriptions = json.dumps([drink[1] for drink in coffee_drinks])

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
        {js_content}
    </script>
    """

# Streamlit UI
def show_coffee_wheel_page():
    st.title("Spin the Coffee Wheel!")
    st.write("Don't know what coffee to drink for your day? Try this wheel!")
    st.write("Click the button to spin the wheel and get a random coffee drink.")
    st.components.v1.html(spin_the_wheel(), height=800)

if __name__ == "__main__":
    show_coffee_wheel_page()