# # Import necessary modules and packages
# from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory
# import cv2
# import face_recognition
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# import os
# import tempfile

# # Create a Flask web application
# app = Flask(__name__)

# # Function definitions

# def authenticate_drive():
#     # Authenticate and create a connection to Google Drive
#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth()
#     drive = GoogleDrive(gauth)
#     return drive

# def upload_to_drive(image_path, folder_id, drive, filename):
#     # Upload a file to Google Drive
#     file1 = drive.CreateFile({'parents': [{'id': folder_id}], 'title': filename})
#     file1.SetContentFile(image_path)
#     file1.Upload()

# def download_from_drive_direct_link(file, destination_path, drive):
#     # Download a file from Google Drive using its direct link
#     try:
#         file_url = file['webContentLink'].replace('view', 'download')
#         response = drive.auth.service.files().get_media(fileId=file['id']).execute()

#         with open(destination_path, 'wb') as f:
#             f.write(response)

#         return True
#     except KeyError as e:
#         print(f"Error getting 'webContentLink' for file {file['title']}: {e}")
#         return False

# def get_file_size(file_path):
#     # Get the file size in megabytes
#     return os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB

# def capture_reference_image(droidcam_url, output_folder, drive_folder_id, drive):
#     # Capture a reference image from a webcam and upload it to Google Drive
#     camera = cv2.VideoCapture(droidcam_url)

#     while True:
#         _, frame = camera.read()

#         # Detect faces in the frame
#         faces = face_recognition.face_locations(frame)
#         for (x, y, width, height) in faces:
#             cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 0), 2)

#         cv2.imshow("DroidCam Camera", frame)
#         key = cv2.waitKey(1)

#         if key == ord("q"):
#             reference_image_path = os.path.join(output_folder, "reference_image.jpg")
#             try:
#                 cv2.imwrite(reference_image_path, frame)
#                 upload_to_drive(reference_image_path, drive_folder_id, drive, "reference_image.jpg")
#                 print(f"Reference image captured and stored in Google Drive.")
#                 break
#             except Exception as e:
#                 print(f"Error capturing or uploading reference image: {e}")

#     camera.release()
#     cv2.destroyAllWindows()
#     return reference_image_path

# def process_images(drive, reference_image_path, google_drive_photos_folder_id, matching_folder_drive_id):
#     # Process images in Google Drive to find matches with the reference image
#     reference_image = face_recognition.load_image_file(reference_image_path)
#     reference_encodings = face_recognition.face_encodings(reference_image)
    
#     if not reference_encodings:
#         print("No face found in the reference image. Please provide an image with a clear frontal face.")
#         return []

#     reference_encoding = reference_encodings[0]
#     print("Reference encoding successfully generated.")

#     matching_images = []

#     for file_list in drive.ListFile({'q': f"'{google_drive_photos_folder_id}' in parents"}).GetList():
#         try:
#             temp_download_path = tempfile.mktemp(suffix=".jpg")  # Temporary file for downloading
#             if download_from_drive_direct_link(file_list, temp_download_path, drive):
#                 current_image = face_recognition.load_image_file(temp_download_path)
#                 face_locations = face_recognition.face_locations(current_image)
#                 face_encodings = face_recognition.face_encodings(current_image, face_locations[:10])

#                 for i, face_encoding in enumerate(face_encodings):
#                     matches = face_recognition.compare_faces([reference_encoding], face_encoding)

#                     if matches[0]:
#                         sanitized_filename = file_list['title'].replace(" ", "_").lower()
#                         print(f"Match found! Uploading matching image: {sanitized_filename}")
#                         upload_to_drive(
#                             temp_download_path,
#                             matching_folder_drive_id,
#                             drive,
#                             f"matching_{sanitized_filename}_{i}.jpg",
#                         )
#                         matching_images.append(sanitized_filename)
#                         break  # Exit the loop after finding a match

#                 os.remove(temp_download_path)  # Remove the temporary file

#         except Exception as e:
#             print(f"Error processing or downloading image {file_list['title']}: {e}")

#     print("Program ended.")

#     if len(matching_images) == 0:
#         print("No photos matched the reference image.")
#     else:
#         return matching_images

# # Flask routes

# @app.route('/')
# def index():
#     # Render the main index page
#     return render_template('face_detection_form.html')

# matching_images_list = []  # Global variable to store matching images

# @app.route('/process-image', methods=['POST'])
# def process_image():
#     global matching_images_list  # Use the global variable
#     reference_image_path = capture_reference_image(droidcam_url, output_folder, drive_folder_id, drive)
#     matching_images_list = process_images(drive, reference_image_path, google_drive_photos_folder_id, matching_folder_drive_id)
#     return redirect(url_for('webone'))

# @app.route('/webone')
# def webone():
#     global matching_folder_drive_id, matching_images

#     # Fetch matching images from the server
#     matching_images = []

#     try:
#         matching_images = [f for f in os.listdir(matching_folder_drive_id) if f.endswith(('.jpg', '.jpeg', '.png'))]
#     except Exception as e:
#         print(f"Error reading matching images: {e}")

#     # Render the webone.html template with the matching images
#     return render_template('webone.html', matching_images=matching_images, os=os)

# # Application entry point
# if __name__ == '__main__':
#     # Authenticate Google Drive and set up folder IDs
#     drive = authenticate_drive()
#     drive_folder_id = '1k5EuM3Rh1Z-ej6AreLOMt8fA2HRckclw'
#     google_drive_photos_folder_id = '1MQd0YZDiwRnG52OfHkmsWbRX4smye8st'
#     matching_folder_drive_id = '12Zs5EAHfod-uJCN7Keb_1ch1o-xG1_j0'
#     output_folder = "reference_image"
#     droidcam_url = "http://192.168.29.77:4747/video"
#     temp_output_folder = "temp_matching_images"

#     # Run the Flask application in debug mode
#     app.run(debug=True)