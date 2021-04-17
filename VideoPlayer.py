#!/usr/bin/env python3

import threading
import cv2
import os
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
    
    os.write(1,(f'Reading frame {count} {success}').encode())
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        producerQ.put(image)
        count+=1
        #gets jpeg and lets you know if its successful or not 
        success,image = vidcap.read()
        os.write(1,(f'reading frame {count} \n').encode())
    os.write(1,(f'frame extraction into producer Q complete\n').encode())

#Dequues and enqueues into consumer queue
def convertToGrayScale():
    count = 0
    while 1:
        if producerQ.isEmpty():
            continue 
        getFrame = producerQ.get() #gets frames from producer Q
        if count ==totalFrames:
            os.write(1,(f'converting the last frame {count}\n').encode())
            break
        #convert grayscale
        grayScaleFrame = cv2.cvtColor(getFrame, cv2.COLOR_BGR2GRAY)
        consumerQ.put(grayScaleFrame) #adds to consumer q 
        os.write(1,(f'Converting frame {count}\n').encode())
    
        count+=1
    os.write(1,(f'convert to grayscale complete\n').encode())
        

def displayFrames():
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while 1:
        if count == totalFrames:
            os.write(1,(f'last frame {count}\n').encode())
            break
        if consumerQ.isEmpty():
            continue 
        # get the next frame
        frame = consumerQ.get()

        os.write(1,(f'Displaying frame {count}\n').encode())        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    os.write(1,(f'Finished displaying all frames\n').encode())
    # cleanup the windows
    cv2.destroyAllWindows()

# display the frames

producerQ = ProducerConsumerQ()

consumerQ = ProducerConsumerQ()

filename = 'clip.mp4'
c = cv2.VideoCapture(filename)
totalFrames = int(c.get(cv2.CAP_PROP_FRAME_COUNT))-1 #gets total number of frames from the file

extractThread = threading.Thread(target= extractFrames,args = (filename, totalFrames))

convertGrayScaleThread = threading.Thread(target = convertToGrayScale)
displayThread = threading.Thread(target = displayFrames)
extractThread.start()
convertGrayScaleThread.start()
displayThread.start()



