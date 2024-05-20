from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory, abort, send_file
import cv2
import face_recognition
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Function definitions
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def upload_to_drive(image_path, folder_id, drive, filename):
    file1 = drive.CreateFile({'parents': [{'id': folder_id}], 'title': filename})
    file1.SetContentFile(image_path)
    file1.Upload()

def download_from_drive_direct_link(file, destination_path, drive):
    try:
        file_url = file['webContentLink'].replace('view', 'download')
        response = drive.auth.service.files().get_media(fileId=file['id']).execute()

        with open(destination_path, 'wb') as f:
            f.write(response)

        return True
    except KeyError as e:
        print(f"Error getting 'webContentLink' for file {file['title']}: {e}")
        return False

def get_file_size(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB

def capture_reference_image(droidcam_url, output_folder, drive_folder_id, drive):
    camera = cv2.VideoCapture(droidcam_url)
    while True:
        _, frame = camera.read()
        cv2.imshow("DroidCam Camera", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            reference_image_path = os.path.join(output_folder, "reference_image.jpg")
            try:
                cv2.imwrite(reference_image_path, frame)
                upload_to_drive(reference_image_path, drive_folder_id, drive, "reference_image.jpg")
                print(f"Reference image captured and stored in Google Drive.")
                break
            except Exception as e:
                print(f"Error capturing or uploading reference image: {e}")

    camera.release()
    cv2.destroyAllWindows()
    return reference_image_path

def process_images(drive, reference_image_path, google_drive_photos_folder_id, matching_folder_drive_id):
    reference_image = face_recognition.load_image_file(reference_image_path)
    reference_encodings = face_recognition.face_encodings(reference_image)
    
    if not reference_encodings:
        print("No face found in the reference image. Please provide an image with a clear frontal face.")
        return []

    reference_encoding = reference_encodings[0]
    print("Reference encoding successfully generated.")

    matching_images = []

    for file_list in drive.ListFile({'q': f"'{google_drive_photos_folder_id}' in parents"}).GetList():
        try:
            temp_download_path = tempfile.mktemp(suffix=".jpg")  # Temporary file for downloading
            if download_from_drive_direct_link(file_list, temp_download_path, drive):
                current_image = face_recognition.load_image_file(temp_download_path)
                face_locations = face_recognition.face_locations(current_image)
                face_encodings = face_recognition.face_encodings(current_image, face_locations[:10])

                for i, face_encoding in enumerate(face_encodings):
                    matches = face_recognition.compare_faces([reference_encoding], face_encoding)

                    if matches[0]:
                        sanitized_filename = file_list['title'].replace(" ", "_").lower()
                        print(f"Match found! Uploading matching image: {sanitized_filename}")
                        upload_to_drive(
                            temp_download_path,
                            matching_folder_drive_id,
                            drive,
                            f"matching_{sanitized_filename}",  # Change the filename format here
                        )
                        matching_images.append(sanitized_filename)
                        break  # Exit the loop after finding a match

            os.remove(temp_download_path)  # Remove the temporary file

        except Exception as e:
            print(f"Error processing or downloading image {file_list['title']}: {e}")

    print("Program ended.")

    if len(matching_images) == 0:
        print("No photos matched the reference image.")
    else:
        return matching_images

# Flask routes

def folder_exists(folder_path):
    return os.path.exists(folder_path)

@app.route('/')
def index():
    return render_template('face_detection_form.html')

matching_images_list = []  # Global variable to store matching images

@app.route('/process-image', methods=['POST'])
def process_image():
    global matching_images_list  # Use the global variable
    reference_image_path = capture_reference_image(droidcam_url, output_folder, drive_folder_id, drive)
    matching_images_list = process_images(drive, reference_image_path, google_drive_photos_folder_id, matching_folder_drive_id)
    return redirect(url_for('webone'))

@app.route('/webone')
def webone():
    global matching_folder_drive_id, drive

    matching_images = []

    # Get the list of files in the matching folder
    file_list = drive.ListFile({'q': f"'{matching_folder_drive_id}' in parents and trashed=false"}).GetList()

    for file in file_list:
        matching_images.append(file['title'])

    # Render the webone.html template with the matching images
    return render_template('webone.html', matching_images=matching_images)


@app.route('/get-matching-image/<filename>')
def get_matching_image(filename):
    folder_id = '1is_pQnhEqyvjBdoZX-8grEBaSHJfdOMH'  # Replace with the actual folder ID
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

    for file in file_list:
        if file['title'] == filename:
            temp_download_path = tempfile.mktemp(suffix=".jpg")  # Temporary file for downloading
            if download_from_drive_direct_link(file, temp_download_path, drive):
                return send_file(temp_download_path, mimetype='image/jpeg', as_attachment=True)

    # Return a 404 response if the image is not found
    abort(404)

if __name__ == '__main__':
    drive = authenticate_drive()
    drive_folder_id = '1k5EuM3Rh1Z-ej6AreLOMt8fA2HRckclw'
    google_drive_photos_folder_id = '1MQd0YZDiwRnG52OfHkmsWbRX4smye8st'
    matching_folder_drive_id = '12Zs5EAHfod-uJCN7Keb_1ch1o-xG1_j0'
    output_folder = "reference_image"
    droidcam_url = "http://192.168.29.77:4747/video"
    temp_output_folder = "temp_matching_images"

    app.run(debug=True)