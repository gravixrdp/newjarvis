from sys import flags
import time
import cv2
import pyautogui as p


def AuthenticateFace():

    flag = ""
    # Local Binary Patterns Histograms
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.read('backend\\auth\\trainer\\trainer.yml')  # load trained model
    cascadePath = "backend\\auth\\haarcascade_frontalface_default.xml"
    # initializing haar cascade for object detection approach
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX  # denotes the font type

    # Mapping of IDs to names (index starts at 0; keep empty for 0 if unused)
    # Extend this list or leave blank entries; we will fallback to "User {id}" if not present.
    names = ['', '', 'Ankit']  # example entries; add your own IDs via training

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # cv2.CAP_DSHOW to remove warning
    cam.set(3, 640)  # set video FrameWidht
    cam.set(4, 480)  # set video FrameHeight

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:

        ret, img = cam.read()  # read the frames using the above created object

        # The function converts an input image from one color space to another
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for(x, y, w, h) in faces:

            # used to draw a rectangle on any image
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # to predict on every single image
            pred_id, accuracy = recognizer.predict(converted_image[y:y+h, x:x+w])

            # Check if accuracy is less them 100 ==> "0" is perfect match
            if (accuracy < 100):
                # Use mapped name if available, else fallback to "User {id}"
                if pred_id < len(names) and names[pred_id]:
                    label = names[pred_id]
                else:
                    label = f"User {pred_id}"
                acc_str = "  {0}%".format(round(100 - accuracy))
                flag = 1
            else:
                label = "unknown"
                acc_str = "  {0}%".format(round(100 - accuracy))
                flag = 0

            cv2.putText(img, str(label), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(acc_str), (x+5, y+h-5),
                        font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        if flag == 1:
            break
            

    # Do a bit of cleanup
    
    cam.release()
    cv2.destroyAllWindows()
    return flag
 