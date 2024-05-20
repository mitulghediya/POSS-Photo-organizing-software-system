import face_recognition
import json
import os

def store_face_encodings(image_path):
    print("Loading image...")
    image = face_recognition.load_image_file(image_path)

    print("Extracting face encoding...")
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        print("No faces found in the provided image.")
        return None

    # Convert NumPy arrays to Python lists
    face_encodings = [enc.tolist() for enc in face_encodings]
    print("Face encodings extracted successfully.")
    return face_encodings

def main():
    # Path to the directory and image file
    base_path = r"C:\Users\lenovo\Desktop\swizzdigi\POSS"
    image_folder = "reference_image"
    image_path = os.path.join(base_path, image_folder, "reference_image.jpg")

    # Get face encodings
    face_encodings = store_face_encodings(image_path)

    if face_encodings:
        # Save face encodings to JSON file
        json_file_path = os.path.join(base_path, image_folder, "reference_image_face_encodings.json")
        print("Saving face encodings to JSON file...")
        with open(json_file_path, 'w') as json_file:
            json.dump(face_encodings, json_file, indent=2)

        print(f"Face encodings stored successfully")

if __name__ == "__main__":
    main()
