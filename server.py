from flask import Flask, request, jsonify, send_from_directory
import json
import os
import base64
from werkzeug.serving import run_simple
from dotenv import load_dotenv
import random

load_dotenv()  # This loads the .env file

app = Flask(__name__, static_folder='frontend')

with open("verses/verses.json", "r") as f:
    verses = json.load(f)

background_dir = "backgrounds"
output_dir = "output"
processed_dir = "processed_backgrounds"

current_verse_index = 0
background_images = os.listdir(background_dir)

os.makedirs(output_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

@app.route('/next-verse')
def next_verse():
    global current_verse_index, background_images

    if current_verse_index >= len(verses):
        return jsonify({"done": True})

    # Check if we've run out of backgrounds
    if len(background_images) == 0:
        # Move all processed backgrounds back to the background_dir
        processed_images = os.listdir(processed_dir)
        for image in processed_images:
            os.rename(os.path.join(processed_dir, image), os.path.join(background_dir, image))
        # Update the list of available background images
        background_images = os.listdir(background_dir)

    verse = verses[current_verse_index]
    background_url = f"/backgrounds/{background_images[current_verse_index % len(background_images)]}"
    current_verse_index += 1

    progress = (current_verse_index / len(verses)) * 100

    return jsonify({
        "verse": verse["text"],
        "reference": verse["reference"],
        "backgroundUrl": background_url,
        "progress": f"{progress:.2f}"
    })

@app.route('/export-image', methods=['POST'])
def export_image():
    global background_images

    data = request.json
    image_data = data['imageData'].replace("data:image/png;base64,", "")
    verse = data['verse']
    reference = data['reference']

    file_name = f"{reference.replace(' ', '_')}.png"
    with open(os.path.join(output_dir, file_name), "wb") as f:
        f.write(base64.b64decode(image_data))

    # Move the used background image to the processed folder
    used_background = background_images[(current_verse_index - 1) % len(background_images)]
    os.rename(os.path.join(background_dir, used_background), os.path.join(processed_dir, used_background))

    # Update the list of available background images
    background_images = os.listdir(background_dir)

    return jsonify({"success": True})

@app.route('/backgrounds/<path:filename>')
def serve_background(filename):
    return send_from_directory(background_dir, filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/google-fonts-key')
def get_google_fonts_key():
    return jsonify({"key": os.getenv('GOOGLE_FONTS_API_KEY')})

@app.route('/random-background')
def random_background():
    if background_images:
        random_image = random.choice(background_images)
        return jsonify({"backgroundUrl": f"/backgrounds/{random_image}"})
    else:
        return jsonify({"error": "No background images available"}), 404

if __name__ == '__main__':
    run_simple('localhost', 8000, app)