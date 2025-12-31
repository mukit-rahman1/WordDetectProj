# Underlined Vocabulary Scanner (YOLO + OCR + Dictionary API)

An app that automatically detects words in the image using a custom YOLO model, runs OCR (Tesseract) on each detected region, and fetches definitions for each extracted word using a free Dictionary API.

This project was inspired by my goal of completing more classical books, and it aims to speed up the process of vocabulary lookup.  
Demo pics at the end of this readme.  

**Pipeline:** Image → YOLO word boxes → preprocess crop → OCR best-guess → de-duplicate → definitions → JSON response -> display


## Project Goals
- To learn to train a custom YOLO model for the recognition of underlined words
- Set up Tesseract OCR for word detection
- To practice the Flask framework
- Understanding Pre-processing techniques (Denoising, CLAHE, Otsu Thresholding, etc.)
- MADE TO MAKE MY LIFE EASIER reading tougher books

## Tech Stack
- **Backend:** Python, Flask
- **Detection:** Ultralytics YOLO (custom model)
- **OCR:** pytesseract + OpenCV
- **Definitions:** dictionaryapi.dev (free)
- **Image Processing:** NumPy, OpenCV

## Installation
### Step 1  
Enter root dir  
cd WordDetectProj
### Optional
step up virutal env  
macOS / Linux:
```
python3 -m venv .venv && source .venv/bin/activate
```
Windows (PowerShell):
```
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
```

### Step 2  
Install Python dependencies 
```
pip install -r requirements.txt
```

### Step 3
Install Tesseract
macOS (Homebrew):  
```
brew install tesseract
```
Ubuntu / Debian:
```
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

Windows:
Install Tesseract, then (if needed) set:
```
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### Step 4
Run the app
```
python app.py
```
## Pictures
It can input this image:  
![in1](https://github.com/mukit-rahman1/WordDetectProj/blob/main/imgs/in1.jpg?raw=true)  
Output:  
![out1](https://github.com/mukit-rahman1/WordDetectProj/blob/main/imgs/out1.png?raw=true)

Input:  
![in2](https://github.com/mukit-rahman1/WordDetectProj/blob/main/imgs/in2.jpg?raw=true)  
Output:  
![out2](https://github.com/mukit-rahman1/WordDetectProj/blob/main/imgs/out2.png?raw=true)
```

