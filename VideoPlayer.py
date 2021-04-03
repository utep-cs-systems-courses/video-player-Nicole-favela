#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

mutex = threading.Lock()
class ProducerConsumerQ():
    def __init__(self):
        self.semaphore = threading.Semaphore(10)
        self.queue = queue.Queue()
    #add to queue
    def put(self,frame):
        self.semaphore.acquire() #gets semaphore and decrements it
        mutex.acquire() 
        self.queue.put(frame)
        mutex.release()
    #retrieve image from queue
    def get(self):
        self.semaphore.release() #increments semaphore
        mutex.acquire()
        frame = self.queue.get()
        mutex.release()
        return frame
    #checks if queue is empty
    def isEmpty(self):
        mutex.acquire()
        isEmpty = self.queue.empty()
        mutex.release()
        return isEmpty
    
    
def extractFrames(fileName, total):
    # Initialize frame count 
    count = 0
    
    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print(f'Reading frame {count} {success}')
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        producerQ.put(image)
        print(f'Reading frame {count}{success}')
        count+=1
        

        # add the frame to the buffer
        #outputBuffer.put(image)
        success,image = vidcap.read()
    print("frame extraction into producer Q complete")

#Dequues and enqueues into consumer queue
def convertToGrayScale():
    count = 0
    while 1:
        if producerQ.isEmpty():
            continue #change to exit???
        getFrame = producerQ.get()
        if count ==totalFrames:
            print(f'converting the last frame {count}')
            break
        #convert grayscale
        grayScaleFrame = cv2.cvtColor(getFrame, cv2.COLOR_BGR2GRAY)
        consumerQ.put(grayScaleFrame)
        print(f'Converting frame {count}')
    
        count+=1
        

def displayFrames():
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while 1:
        if count == totalFrames:
            print(f'last frame {count}')
            break
        if consumerQ.isEmpty():
            continue 
        # get the next frame
        frame = consumerQ.get()

        print(f'Displaying frame {count}')        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print('Finished displaying all frames')
    # cleanup the windows
    cv2.destroyAllWindows()

# filename of clip to load
#filename = 'clip.mp4'

# shared queue  
#extractionQueue = queue.Queue()

# extract the frames
#extractFrames(filename,extractionQueue, 72)

# display the frames
print("before producer Q")
producerQ = ProducerConsumerQ()
print("after produecer")
consumerQ = ProducerConsumerQ()
print("after consumer q")
filename = 'clip.mp4'
c = cv2.VideoCapture(filename)
totalFrames = int(c.get(cv2.CAP_PROP_FRAME_COUNT))-1 #gets total number of frames from the file
print("anything")
extractThread = threading.Thread(target= extractFrames,args = (filename, totalFrames))
print("anything you want")
convertGrayScaleThread = threading.Thread(target = convertToGrayScale)
print("after gray scale thread")
displayThread = threading.Thread(target = displayFrames)
print("after display thread")
extractThread.start()
print("after extract thread")
convertGrayScaleThread.start()
print("after gray scale thread")
displayThread.start()
print("done")


