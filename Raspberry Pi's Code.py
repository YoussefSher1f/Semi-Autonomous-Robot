import zmq
import cv2
import paho.mqtt.publish as mqtt_publish

# MQTT broker details
mqtt_broker = "broker.emqx.io"
mqtt_port = 1883

# QR code detection Method
detector = cv2.QRCodeDetector()

# Open the camera
cap = cv2.VideoCapture(-1)  # Assuming the correct camera index is -1

if _name_ == '_main_':
    # This creates an Infinite loop to keep your camera searching for data at all times
    while True:
        # Below is the method to get an image of the QR code
        _, img = cap.read()

        # Below is the method to read the QR code by detecting the bounding box coords and decoding the hidden QR data
        data, bbox, _ = detector.detectAndDecode(img)

        # This is how we get that Blue Box around our Data. This will draw one, and then Write the Data along with the top
        if bbox is not None:
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i + 1) % len(bbox)][0]), color=(155, 255, 0),
                         thickness=6)
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_COMPLEX, 2,
                        (59, 59, 191), 4)

            # Below prints the found data to the console and publishes it to the corresponding MQTT topic
            if data:
                print("Room Number:", data)
                mqtt_publish.single("inTopic", payload=data, hostname=mqtt_broker, port=mqtt_port)

        # Below will display the live camera feed to the Desktop on Raspberry Pi OS preview
        cv2.imshow("NewCodes", img)

        # At any point if you want to stop the Code, all you need to do is press 'q' on your keyboard
        if cv2.waitKey(1) == ord("q"):
            break

# When the code is stopped, the below closes all the applications/windows that the above has created
cap.release()
cv2.destroyAllWindows()
