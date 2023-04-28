from flask import Flask, render_template, request, redirect, url_for, session 
from google.cloud import storage
from ultralytics import YOLO
import os

app = Flask(__name__)
storage_client = storage.Client()
bucket_name = 'flaskwebapptest'
bucket = storage_client.get_bucket(bucket_name)
app.secret_key = "justdortesting"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    print(f"test2")
    uploaded_files = request.files.getlist("file")
    session['uploaded_image_paths'] = []

    for file in uploaded_files:
        blob = bucket.blob(file.filename)
        blob.upload_from_string(file.read(), content_type=file.content_type)
        image_url = f"https://storage.googleapis.com/{bucket.name}/{file.filename}"
        session['uploaded_image_paths'].append(image_url)

    return render_template('success.html', message="The files have been successfully uploaded to the system.")

@app.route('/detect', methods=['POST'])
def detect_objects():
    print(f"test3")
    # Get the last uploaded images from the session
    last_uploaded_images = session.get('uploaded_images_paths', [])

    output_files = []

    # Run detection on the last uploaded images
    for image_path in last_uploaded_images:
        print(f"{image_path}")
        model = YOLO("best.pt")  # load a pretrained model (recommended for training)
        model.predict(image_path, save=True, save_txt=True, imgsz=320, conf=0.1)

        # Output files are saved automatically by the YOLO program
        image_file_name = os.path.basename(image_path)
        image_name_without_extension, _ = os.path.splitext(image_file_name)
        output_image_path = f'runs/detect/predict/{image_file_name}'
        output_csv_path = f'runs/detect/predict/label/{image_name_without_extension}.txt'

        # Move output files to the 'static' folder
        os.rename(output_image_path, f'static/{image_file_name}')
        os.rename(output_csv_path, f'static/{image_name_without_extension}.csv')

        # Generate download links
        output_image_url = url_for('static', filename=image_file_name)
        output_csv_url = url_for('static', filename=f'{image_name_without_extension}.csv')

        output_files.append((output_image_url, output_csv_url))

    return render_template('results.html', output_files=output_files)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
