import face_recognition
import json
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

def store_face_encodings(image_path, json_file_path):
    print("Loading image...")
    if os.path.exists(image_path):
        print("Image found.")
    else:
        print(f"Image not found at {image_path}. Exiting.")
        return None

    image = face_recognition.load_image_file(image_path)

    print("Detecting face in the image...")
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        print("No faces found in the provided image.")
        return None

    print("Face found!")
    print("Extracting face encoding...")
    face_encodings = face_recognition.face_encodings(image, face_locations)

    # Convert NumPy arrays to Python lists
    face_encodings = [enc.tolist() for enc in face_encodings]

    # Save face encodings to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(face_encodings, json_file, indent=2)

    print(f"Face encodings stored successfully in {json_file_path}")

    # Upload the file to Google Drive
    upload_to_drive(json_file_path)

def upload_to_drive(file_path):
    # Provide the absolute path to your 'client_secrets.json' file
    client_secrets_file = r'C:\Users\lenovo\Desktop\swizzdigi\POSS\client_secrets.json'

    # Load your credentials from the 'client_secrets.json' file
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, ['https://www.googleapis.com/auth/drive.file'])

    # Run the flow using the server strategy.
    creds = flow.run_local_server(port=0)

    # Build the drive service
    drive_service = build('drive', 'v3', credentials=creds)

    # Create a MediaFileUpload object and specify the MIME type of the file
    media = MediaFileUpload(file_path, mimetype='application/json')

    # Call the drive service files().create() method and pass the MediaFileUpload object to it
    request = drive_service.files().create(media_body=media, body={'name': os.path.basename(file_path)})

    # Execute the request
    request.execute()

    print(f"File uploaded successfully to Google Drive")

def main():
    # Path to the directory and image file
    base_path = r"C:\Users\lenovo\Desktop\swizzdigi\POSS"
    image_folder = "reference_image"
    image_path = os.path.join(base_path, image_folder, "reference_image.jpg")
    
    # JSON file path (in the same directory as the image)
    json_file_path = os.path.join(base_path, image_folder, "face_encodings.json")

    # Get face encodings
    store_face_encodings(image_path, json_file_path)

if __name__ == "__main__":
    main()
