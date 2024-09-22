# Bible Instagram Post Generator

<p align="center">
  <img src="1.webp" width="45%" alt="Sample Image 1">
  <img src="2.webp" width="45%" alt="Sample Image 2">
</p>

## Introduction

The Bible Instagram Post Generator is a web application that allows users to create visually appealing images with Bible verses for sharing on social media platforms like Instagram. This guide will walk you through the setup process and how to use the application.

## Features

- Generates images with Bible verses and references
- Customizable visual effects (vignette, grain, brightness)
- Adjustable font styles and sizes (using Google Fonts API)
- Background image selection
- Batch processing of multiple verses

## Setup

1. Clone the repository to your local machine.

2. Install the required dependencies. Make sure you have Python installed, then run:
   ```
   pip install flask python-dotenv
   ```

3. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your Google Fonts API key:
     ```
     GOOGLE_FONTS_API_KEY=your_api_key_here
     ```

4. Prepare your assets:
   - Place background images in the `backgrounds` directory
   - Ensure you have the `verses/verses.json` file with your desired Bible verses

5. Run the server:
   ```
   python server.py
   ```

6. Open your web browser and navigate to `http://localhost:8000`

## Using the Application

### Main Interface

The main interface consists of two parts:
1. The image preview area
2. The control panel

### Customizing the Image

You can adjust various aspects of the image using the control panel:

1. Vignette Effect:
   - Size
   - Intensity
   - Blur

2. Grain Effect:
   - Intensity
   - Size

3. Brightness

4. Font Selection:
   - Verse Font
   - Reference Font

5. Font Sizes:
   - Verse Font Size
   - Reference Font Size

As you adjust these settings, the preview will update in real-time.

### Generating Images

1. Once you're satisfied with the settings, click the "Start Generation" button.

2. The application will process all verses in the `verses.json` file, creating an image for each one.

3. A progress bar will show the status of the generation process.

4. Generated images will be saved in the `output` directory.

## Code Overview

### Frontend

The frontend is built using HTML, CSS, and JavaScript.


### Verse Processing

The application uses a separate Python script to process and prepare verses: `verses/extract.py`.

This script takes a list of verse references from `verses/verse_references.txt` and extracts the verse text from the Bible, currently using the New Living Translation (NLT).


## Customization

1. To add or modify verses, edit the `verses/verses.json` file.

2. To change available background images, add or remove images from the `backgrounds` directory.

3. To modify the visual effects, edit the shader code in `frontend/index.js`:


## Troubleshooting

1. If images are not generating, check the browser console for any JavaScript errors.

2. Ensure that the `backgrounds` and `output` directories exist and have the correct permissions.

3. If fonts are not loading, verify that your Google Fonts API key is correct in the `.env` file.
