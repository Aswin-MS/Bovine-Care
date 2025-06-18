import cv2
import numpy as np
from tensorflow.keras.models import load_model
from ultralytics import YOLO
from PIL import Image
import os
import time
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile

app = Flask(__name__, static_folder='assets', template_folder='templates')

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'assets/processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load models
try:
    model_cow = YOLO('backend/cowModel.pt')
    print("Cow detection model loaded successfully")
except Exception as e:
    print(f"Failed to load cow detection model: {e}")
    exit(1)

try:
    classification_model = load_model('backend/best_model.keras')
    print("Lumpy Skin Disease classification model loaded successfully")
except Exception as e:
    print(f"Failed to load Lumpy Skin Disease model: {e}")
    exit(1)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_np):
    try:
        # Detect cows using the YOLO model
        detections = model_cow(Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)))
        
        for box in detections[0].boxes.xyxy.cpu().numpy():
            x1, y1, x2, y2 = map(int, box[:4])
            # Ensure coordinates are within image bounds
            h, w = image_np.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x1 >= x2 or y1 >= y2:
                continue  # Skip invalid boxes
                
            # Crop and preprocess the detected region
            crop = image_np[y1:y2, x1:x2]
            crop_resized = cv2.resize(crop, (224, 224))
            crop_array = np.expand_dims(crop_resized, axis=0) / 255.0
            
            # Get prediction from the classification model
            prediction = classification_model.predict(crop_array)
            prob = prediction[0][0]
            threshold = 0.5
            # If the probability is above the threshold, classify as Lumpy Skin Disease
            if prob > threshold:
                label = "Healthy"
                confidence = (prob) * 100
                color = (0, 255, 0)  # Green for healthy
            else:
                label = "Lumpy Skin Disease"
                confidence = (1 - prob) * 100
                color = (0, 0, 255)  # Red for disease
                

            # Draw the bounding box and label on the image
            cv2.rectangle(image_np, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image_np, f"{label} ({confidence:.2f}%)", (x1, max(y1 - 10, 10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image_np
    except Exception as e:
        print(f"Image processing error: {e}")
        return None

def process_video(input_path, output_path):
    try:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Failed to open video file")

        # Get video properties
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = max(1, int(cap.get(cv2.CAP_PROP_FPS)))  # Ensure valid FPS

        # Ensure dimensions are even for codec compatibility
        frame_width -= frame_width % 2
        frame_height -= frame_height % 2

        # Use H.264 codec (good compatibility)
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        output_path = output_path if output_path.endswith('.mp4') else output_path + '.mp4'

        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        if not out.isOpened():
            cap.release()
            raise Exception("Failed to create video writer")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame to adjusted dimensions
            frame = cv2.resize(frame, (frame_width, frame_height))
            
            # Process frame (ensure BGR format)
            processed_frame = process_image(frame)
            if processed_frame is not None:
                processed_frame = cv2.resize(processed_frame, (frame_width, frame_height))
                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
                out.write(processed_frame)

        cap.release()
        out.release()
        return True

    except Exception as e:
        print(f"Video processing error: {e}")
        print(f"Frame size: {frame_width}x{frame_height}, FPS: {fps}")
        return False

def process_and_visualize(file_stream, filename):
    try:
        is_video = filename.lower().endswith(('mp4', 'mov'))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

        if is_video:
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file_stream.save(temp_path)

            output_filename = f'processed_{timestamp}.mp4'
            output_path = os.path.join(PROCESSED_FOLDER, output_filename)

            if process_video(temp_path, output_path):
                os.remove(temp_path)
                return url_for('serve_processed', filename=output_filename)
            else:
                os.remove(temp_path)
                return None
        else:
            image = Image.open(file_stream).convert('RGB')
            image_np = np.array(image)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            processed_image = process_image(image_np)
            if processed_image is not None:
                output_filename = f'processed_{timestamp}.jpg'
                output_path = os.path.join(PROCESSED_FOLDER, output_filename)
                cv2.imwrite(output_path, processed_image)
                return url_for('serve_processed', filename=output_filename)
            return None
        
    except Exception as e:
        print(f"Processing error: {e}")
        return None

@app.route('/')
def home():
    return render_template('index1.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/doctorlogin')
def doctor_login():
    return render_template('doctorlogin.html')

@app.route('/farmerdashboard')
def farmer_dashboard():
    return render_template('farmerdashboard.html')
@app.route("/doctordashboard")
def doctor_dashboard():
    return render_template("doctordashboard.html")

@app.route('/farmerlogin')
def farmer_login():
    return render_template('farmerlogin.html')

@app.route('/farmerregister')
def farmer_register():
    return render_template('farmerregister.html')

@app.route('/assets/processed/<path:filename>')
def serve_processed(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route('/predict', methods=['POST'])
def upload_image():
    if 'files' not in request.files:
        return jsonify({'error': 'No file uploaded', 'results': []}), 400

    results = []
    for file in request.files.getlist('files'):
        if file.filename == '':
            results.append({'filename': 'empty', 'status': 'No file selected', 'processed_file': None})
            continue

        if not allowed_file(file.filename):
            results.append({'filename': file.filename, 'status': 'Invalid file type', 'processed_file': None})
            continue

        try:
            processed_path = process_and_visualize(file, file.filename)
            if processed_path:
                results.append({
                    'filename': file.filename,
                    'status': "Successfully Analysed",
                    'processed_file': processed_path
                })
            else:
                results.append({
                    'filename': file.filename,
                    'status': "Processing failed",
                    'processed_file': None
                })
        except Exception as e:
            results.append({
                'filename': file.filename,
                'status': f"Error: {str(e)}",
                'processed_file': None
            })

    return jsonify({'results': results})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
