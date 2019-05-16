import requests
import json
import argparse
import imutils
import time as ti
import cv2
from datetime import datetime, time
import cloudinary.uploader
from picamera.array import PiRGBArray
from picamera import PiCamera
import signal
import config

now = datetime.now()
now_time = now.time()

time_between_resets = 10 #mins
time_between_updates = 30 #secs


ti.sleep(1)
print("starting")

def send_cloudinary():
    try:
        with Timeout(3):
            cloudinary.uploader.upload("output.jpg", width="640", height="480", public_id=config.CLOUDINARY_PUBLIC_ID,
                                       api_key=config.CLOUDINARY_API_KEY, api_secret=config.CLOUDINARY_API_SECRET,
                                       cloud_name=config.CLOUDINARY_CLOUD_NAME, version="v1539323395")
            print("sent image to cloud")
    except Exception as e:
        print(e)


def send_numpeople(npeople, lat='-27.466217', long='153.027335'):
    """Sends data to the RAPIDiot Dashboard"""
    payload = "{\"num_people\":"+str(npeople)+", \"lat\":"+lat+", \"long\":"+long+"}"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    requests.request("POST", config.RAPIDIOT_URL, data=payload, headers=headers)

def get_authorisation():
    """Gets Auth token to use the human detection api"""
    querystring = {"grant_type": "client_credentials"}
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", config.AUTH_URL, auth = (config.CLIENTID, config.CLIENTSECRET), headers=headers, params=querystring, stream=True)
    print(response.text)
    responseJSON = json.loads(response.text)
    token = responseJSON['access_token']
    return token

def classify_image(img_path, img_result):
    """Sends image to human detection api and returns the number of people in the image"""
    token = get_authorisation()
    headers = {'Authorization': 'Bearer ' + token}
    files = {'file': (img_path,open('person.png','rb'),'image/png')}

    if img_result:
        url = config.DETECTION_URL + "format:image"
        r = requests.post(url, headers=headers, files=files)
        if r.status_code == 200:
            with open('output.jpg', 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    else:
        url = config.DETECTION_URL
        r = requests.post(url, headers=headers, files=files)
        responseJSON = json.loads(r.text)
        print(responseJSON)
        if r.status_code == 200:
            num_people = responseJSON['num_detections']
            return num_people

class Timeout():
    """Timeout class using ALARM signal."""

    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)  # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
ti.sleep(0.25)

# initialize the first frame in the video stream
firstFrame = None

var_time = ti.time()
update_time = ti.time()

process = None
running = False



# loop over the frames of the video
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True): #while True:
    if now_time >= time(8,00) and now_time <= time(18,00):
        # grab the current frame and initialize the occupied/unoccupied
        # text
        text = "Unoccupied"

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        try:
            image = frame.array
        except:
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(image, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        #firstFrame = background_frame()
        if ti.time() - var_time > time_between_resets * 60:
            print(ti.time() - var_time)
            firstFrame = None
            var_time = ti.time()
            print("reset")

        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            rawCapture.truncate(0)
            continue

        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < args["min_area"]:
                rawCapture.truncate(0)
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        if text == "Unoccupied":
            if ti.time() - update_time > time_between_updates:
                print("send to  0 to IOT --------------", ti.time() - update_time)
                send_numpeople(0)
                update_time = ti.time()
            print("There is Nobody there")
        else:
            if ti.time() - update_time > time_between_updates:
                print("send to image to cloudinary --------------", ti.time() - update_time)
                update_time = ti.time()

                cv2.imwrite('person.png', image)

                people = classify_image("person.png", False)
                classify_image("person.png", True)
                print("total ml", ti.time() - update_time)

                send_cloudinary()

                send_numpeople(people)
            print("There is a PERSON there")

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key is pressed, break from the lop
        if key == ord("q"):
            break


    else:
        ti.sleep(30 * 60)
        # if the video argument is None, then we are reading from webcam
        # otherwise, we are reading from a video file
    rawCapture.truncate(0)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
