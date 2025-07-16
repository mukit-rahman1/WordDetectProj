import os
from pathlib import Path
import requests
from flask import Flask, request, render_template, jsonify, Response
from typing import Union, Tuple
from ultralytics import YOLO
import cv2
import pytesseract
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path('uploads/')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """Preprocess image region for better OCR accuracy."""
    # convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # scale up the image to improve OCR
    scale_factor = 2
    gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # increase contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # denoise
    gray = cv2.fastNlMeansDenoising(gray)

    # binarization with Otsu's method
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # dilate to connect components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    binary = cv2.dilate(binary, kernel, iterations=1)

    return binary

@app.route('/')
def index() -> str:
    return render_template('index.html')

# Load the YOLO model once when the app starts
model_path = Path(__file__).parent / 'my_model' / 'my_model.pt'
model = YOLO(model_path, task='detect')

def get_word_definition(word):
    """Get the definition of a word using the Dictionary API."""
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            # get all meanings
            meanings = []
            for entry in data[0]['meanings']:
                part_of_speech = entry.get('partOfSpeech', '')
                definitions = [d['definition'] for d in entry.get('definitions', [])] 
                if definitions:
                    meanings.append({
                        'part_of_speech': part_of_speech,   # part of speech
                        'definitions': definitions[:2]  # limit to first 2 definitions
                    })
            return {
                'success': True,
                'meanings': meanings
            }
        return {
            'success': False,
            'error': 'Definition not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/upload', methods=['POST'])
def upload_file() -> Union[Response, Tuple[Response, int]]: 
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = app.config['UPLOAD_FOLDER'] / file.filename
        file.save(str(filepath))

        detected_words = []
        try:
            # read the image with cv2
            frame = cv2.imread(str(filepath))
            if frame is None:
                return jsonify({'error': 'Could not read image file'}), 500

            # run YOLO inference with the model
            results = model(frame, verbose=False)

            # process results
            for r in results:
                boxes = r.boxes.cpu().numpy()
                for box in boxes:
                    # get coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # extract the region with a larger margin
                    margin = 5
                    y1 = max(0, y1 - margin)
                    y2 = min(frame.shape[0], y2 + margin)
                    x1 = max(0, x1 - margin)
                    x2 = min(frame.shape[1], x2 + margin)
                    word_region = frame[y1:y2, x1:x2]
                    
                    # skip if region is too small
                    if word_region.shape[0] < 10 or word_region.shape[1] < 10:
                        continue
                    
                    # preprocess the region
                    processed = preprocess_for_ocr(word_region)
                    
                    # try multiple OCR configurations and take the best result
                    configs = [
                        '--psm 7 --oem 3',  # Single line of text
                        '--psm 8 --oem 3',  # Single word
                        '--psm 6 --oem 3'   # Uniform block of text
                    ]
                    
                    best_word = ""
                    highest_conf = -1
                    
                    for config in configs:
                        # get detailed OCR data
                        data = pytesseract.image_to_data(
                            processed,
                            config=config,
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # find the word with highest confidence
                        for i, conf in enumerate(data['conf']):
                            if conf > highest_conf and data['text'][i].strip():
                                word = ''.join(c for c in data['text'][i] if c.isalpha()).strip()
                                if word:
                                    highest_conf = conf
                                    best_word = word
                    
                    if best_word:  # only add non-empty words
                        detected_words.append(best_word.lower())  # convert to lowercase for consistency

            # remove duplicates while preserving order
            detected_words = list(dict.fromkeys(detected_words))

            # get definitions for each word
            word_data = []
            for word in detected_words:
                definition_data = get_word_definition(word)
                word_data.append({
                    'word': word,
                    'definition_data': definition_data
                })

            # clean up the uploaded file
            os.remove(str(filepath))

            return jsonify({
                'status': 'success',
                'words': word_data
            })

        except Exception as e:
            # clean up the file in case of error
            if os.path.exists(str(filepath)):
                os.remove(str(filepath))
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file'}), 400  # add this line to handle all other cases

if __name__ == '__main__':
    app.run(debug=True)  