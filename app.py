import os
import requests
from flask import Flask, request, render_template, jsonify

from ultralytics import YOLO
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# Load the YOLO model once when the app starts
# Update this path to your model file
model_path = os.path.join(os.path.dirname(__file__), 'my_model', 'my_model.pt')
model = YOLO(model_path, task='detect')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # --- Integrate your model here ---
        detected_words = []
        try:
            # Read the image
            frame = cv2.imread(filepath)
            if frame is None:
                return jsonify({'error': 'Could not read image file'}), 500

            # Run YOLO inference
            results = model(frame, verbose=False)

            # Process results
            for r in results:
                boxes = r.boxes.cpu().numpy()  # Get boxes on CPU in numpy format
                for box in boxes:
                    detected_words.append(model.names[int(box.cls[0])])
        except Exception as e:
            return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

        # --- Integrate dictionary lookup here ---
        # For each detected word, look up its definition using a dictionary API
        # Store words and definitions in a dictionary or list of dictionaries
        # Example:
        # word_definitions = {}
        # for word in detected_words:
        #     definition = get_definition_from_api(word) # Function to fetch definition
        #     word_definitions[word] = definition

        word_definitions = {}
        for word in detected_words:
            api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    # Extract the first definition found (you might want to be more sophisticated here)
                    definition = data[0]['meanings'][0]['definitions'][0]['definition']
                    word_definitions[word] = definition
                else:
                    word_definitions[word] = "Definition not found."
            except requests.exceptions.RequestException as e:
                word_definitions[word] = f"Error fetching definition: {e}"


        # Clean up the uploaded file (optional)
        # os.remove(filepath)

        return jsonify({'status': 'success', 'definitions': word_definitions})

if __name__ == '__main__':
    # For production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True)