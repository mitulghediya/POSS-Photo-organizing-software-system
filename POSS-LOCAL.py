import cv2
import face_recognition
import os

# DroidCam URL for video streaming (replace 'your_droidcam_ip' and 'your_droidcam_port' with your actual values)
droidcam_url = "http://192.168.29.77:4747/video"

# Create a folder named "reference_image" if it doesn't exist
output_folder = "reference_image"
os.makedirs(output_folder, exist_ok=True)

# Open the DroidCam camera
camera = cv2.VideoCapture(droidcam_url)

# Load Haar Cascade XML file for face detection
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
clf = cv2.CascadeClassifier(cascade_path)

# Capture and store a reference image when 'q' key is pressed
while True:
    # Read a frame from the DroidCam camera
    _, frame = camera.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = clf.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw rectangles around the detected faces
    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 0), 2)

    # Display the frame
    cv2.imshow("DroidCam Camera", frame)

    # Capture and store a reference image when 'q' key is pressed
    key = cv2.waitKey(1)
    if key == ord("q"):
        reference_image_path = os.path.join(output_folder, "reference_image.jpg")
        cv2.imwrite(reference_image_path, frame)
        print(f"Reference image captured and stored as {reference_image_path}.")
        break

# Release the DroidCam camera and close the OpenCV window
camera.release()
cv2.destroyAllWindows()

# Print program start
print("Program started.")

# the reference image
reference_image = face_recognition.load_image_file(reference_image_path)

# Checks if faces are found in the reference image
reference_encodings = face_recognition.face_encodings(reference_image)
if len(reference_encodings) > 0:
    reference_encoding = reference_encodings[0]
    print("Reference encoding successfully generated.")
else:
    print("No face found in the reference image. Please provide an image with a clear frontal face.")
    exit()

# Folder containing your photos
photos_folder = r"C:\Users\lenovo\Desktop\swizzdigi\POS\Photos"

# Create a folder to store matching images
matching_folder = "MatchingImages"
os.makedirs(matching_folder, exist_ok=True)

# List to store matching images
matching_images = []

# List to store original images
original_images = []

# Iterate through each file in the folder
for filename in os.listdir(photos_folder):
    file_path = os.path.join(photos_folder, filename)

    # Check if the file is an image
    if os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
        # Check the file size
        file_size = os.path.getsize(file_path)
        if file_size < 5 * 1024 * 1024:  # Size is in bytes
            print(f"Processing image: {filename}")

            # Load the current image in RGB format
            current_image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)

            # Find face locations and encodings in the current image using HOG model
            print("Detecting faces in the current image...")
            face_locations = face_recognition.face_locations(current_image, model="hog")
            face_encodings = face_recognition.face_encodings(current_image, face_locations)

            if face_encodings:  # Check if face_encodings is not empty
                # Compare face encodings
                print("Comparing face encodings...")
                matches = face_recognition.compare_faces([reference_encoding], face_encodings[0])

                if matches[0]:
                    print(f"Match found! Saving matching image: {filename}")
                    # Save the matching image to the folder in RGB format
                    matching_image_path = os.path.join(matching_folder, f"matching_{filename}")
                    cv2.imwrite(matching_image_path, cv2.cvtColor(current_image, cv2.COLOR_RGB2BGR))

                    # Append the matching image to the list
                    matching_images.append(current_image.copy())

                # Append the original image to the list
                original_images.append(current_image.copy())
        else:
            print(f"Skipping image {filename} as it exceeds 5 MB.")

# Print program end
print("Program ended.")

# Check if any matching images were found
if len(matching_images) == 0:
    print("No photos matched the reference image.")
else:
    # Wait for a key press before closing all windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
