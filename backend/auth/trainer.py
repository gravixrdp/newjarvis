import cv2
import numpy as np
from PIL import Image #pillow package
import os

path = os.path.join('backend', 'auth', 'samples') # Path for samples already taken

recognizer = cv2.face.LBPHFaceRecognizer_create() # Local Binary Patterns Histograms
detector = cv2.CascadeClassifier(os.path.join("backend", "auth", "haarcascade_frontalface_default.xml"))
#Haar Cascade classifier is an effective object detection approach


def Images_And_Labels(path): # function to fetch the images and labels
    # Ensure path exists and is a directory
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Samples directory not found: {path}. Run sample.py first to create it.")

    # Only include image files
    imagePaths = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    faceSamples=[]
    ids = []

    for imagePath in imagePaths: # to iterate particular image path
        gray_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_arr = np.array(gray_img,'uint8') #creating an array

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_arr)

        for (x,y,w,h) in faces:
            faceSamples.append(img_arr[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

print ("Training faces. It will take a few seconds. Wait ...")

faces,ids = Images_And_Labels(path)
recognizer.train(faces, np.array(ids))

# Ensure trainer directory exists
trainer_dir = os.path.join('backend', 'auth', 'trainer')
os.makedirs(trainer_dir, exist_ok=True)
recognizer.write(os.path.join(trainer_dir, 'trainer.yml'))  # Save the trained model as trainer.yml

print("Model trained, Now we can recognize your face.")
 