#!/usr/bin/env python3

def VideoCrop(name, path):
    import cv2
    import numpy as np
    import os
    import subprocess
    font = cv2.FONT_HERSHEY_SIMPLEX
    face_cascade = cv2.CascadeClassifier('./demos/web/haarcascade_frontalface_default.xml')
    upper_cascade = cv2.CascadeClassifier('./demos/web/haarcascade_upperbody.xml')
    eye_cascade = cv2.CascadeClassifier('./demos/web/haarcascade_eye.xml')
#    videodir = path + "/"
#    videoName= input("Enter the video name: ")
#    videoName = "Song3.mp4"
    path = "/home/ubuntu/OpenFace/openface/demos/web/dataset/video/Song3.mp4"
    videoName = path
    try:
        cap = cv2.VideoCapture(videoName)
        print('Camera loading complete')
    except:
        print('Camera loading fail')
        return
    absroute = "./../../dataset/data/"
    absroute += name
    print("=========================" + path +"===============================")
    print ("==========================" + absroute + "=============================")
    if not os.path.isdir(absroute):
        os.mkdir(absroute)
    ## count = 1
    facecnt = 1
    uppercnt = 1
    eyecnt = 1
    cv2.namedWindow('Detect')
    ## fileName = "./" + targetNaame + "/" + targetName
    fileName =  absroute + "/" + name 
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 2, 0, (30, 30))
        uppers = upper_cascade.detectMultiScale(gray, 1.3, 2, 0, (30,30))
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 2, 0, (30,30))

        flag = 0;
        for (faceX, faceY, face_width, face_height) in faces:
            for(upperX, upperY, upper_width, upper_height) in uppers:
                if(upperX < faceX and upperX + upper_width > faceX + face_width and
                            upperY < faceY and upperY + upper_height > faceY + face_height):
                    flag = 1
                    img_trim = frame[upperY:upperY + upper_height, upperX:upperX + upper_width]
                    #ImageName = fileName + "_upper/" + targetName + str(uppercnt) + ".jpg"
                    # cv2.imwrite(ImageName, img_trim)
                    cv2.imwrite(fileName + str(uppercnt) + ".jpg", img_trim)
                    uppercnt = uppercnt+1
                    break

            if( flag == 1):
                break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 255:
            break;
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    VideoCrop()
