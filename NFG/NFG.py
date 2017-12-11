#!/usr/bin/env python3
import subprocess
import sys

def Train():
    proc = subprocess.Popen(['./util/align-dlib.py', './demos/web/dataset/data', 
        'align', 'outerEyesAndNose',
        './../../dataset/align/', 
        '--size', '96'],
        stdout = subprocess.PIPE, stderr = subprocess.PIPE
        )
    out, err = proc.communicate()
    print('==========ALIGN THE IMAGE COMPLETE==========')
    proc = subprocess.Popen(['./batch-represent/main.lua', 
        '-outDir', './demos/web/dataset/embedding/', 
        '-data', './demos/web/dataset/align/'], 
        stdout = subprocess.PIPE, stderr = subprocess.PIPE
        )

    out, err = proc.communicate()
    print('==========EMBEDDING IMAGE COMPLETE==========')
    proc = subprocess.Popen(['rm', './demos/web/dataset/align/cache.t7'])

    out, err = proc.communicate()
    proc = subprocess.Popen(['./demos/classifier.py', 'train', './demos/web/dataset/embedding/'],
                stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    
    out, err = proc.communicate()
    print ("==========TRAIN IMAGES COMPLETE==========")


def Compare(path):
    global pre_name
    dirname = path
    proc = subprocess.Popen(['./demos/classifier.py', 
        'infer', './demos/web/dataset/embedding/classifier.pkl', 
        dirname], 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE
    )

    out, err = proc.communicate()
    name, confidence = out.split()
    pre_name = name
    return name, confidence, dirname
    

if __name__ == "__main__":
    while True:
        check = input("Insert input Data(I) or Training(T) or Compare(C) or QUIT(Q) : ")
#       if check == 'I':
#          detect.faceDetect()
        if check == 'T':
            Train()
        elif check == 'Q':
            break
        elif check == 'C':
            Compare()
        else:
            print("INPUT ERROR")

