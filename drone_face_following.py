import sys
import traceback
import tellopy
import av
import cv2  
import numpy
import time

auto=True # auto track
face_detect = True



def main():
    frame_skip = 300 # skip first 300 frames
    last_time=0.0 # track time command last issued
    speed = 10 # default movement speed
    speed2 = 10
    margin=50 # how far from center before rotating
    target_area = 10000 # area of target size (pixels) to maintain
    drone = tellopy.Tello()

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        container = av.open(drone.get_video_stream())
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


        loop=True
        
        while loop:
                   
            for frame in container.decode(video=0):
                k = cv2.waitKey(1)
                #print(k)
                if k == 52: # right arrow - right
                    print('right')
                    drone.right(speed)
                elif k == 54: # left arrow - left
                    print('left')
                    drone.left(speed) 
                elif k == 56: # up arrow - forward
                    print('up')
                    drone.forward(speed) 
                elif k == 50: # down arrow - backward
                    print('down')
                    drone.backward(speed)
                elif chr(k&0xff) == 'a':    #takeoff
                    print('a - takeoff')              
                    drone.takeoff()
                elif chr(k&0xff) == 'l':    #land
                    print('l - land')
                    drone.land()
                elif chr(k&0xff) == 'f':    #forward
                    print('forward')
                    drone.forward(speed)                  
                elif chr(k&0xff) == 'b':    #backward
                    print('backward')
                    drone.backward(speed)
                elif chr(k&0xff) == 'q':    #counter clockwise
                    print('q - counter clockwise')
                    drone.counter_clockwise(speed)                    
                elif chr(k&0xff) == 'p':    #clock wise
                    print('p - clockwise')
                    drone.clockwise(speed)
                elif chr(k&0xff) == 'u':    #up
                    print('u - up')     
                    drone.up(speed)
                elif chr(k&0xff) == 'n':     #dowN
                    print('n -down')
                    drone.down(speed)
                elif chr(k&0xff) == 'm':   # m - palm land
                    print('m - palm land')
                    drone.palm_land()      
                elif chr(k&0xff) == 't':   # t - take picture
                    print('t - take picture')
                    drone.take_picture()                
                elif k&0xff ==  27:         # esc -- quit
                        loop=False
                        break

                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()  
                
                if face_detect:
                    image = numpy.array(frame.to_image())
                    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    face_detected=False
                    faces = face_cascade.detectMultiScale(
                                gray,
                                scaleFactor=1.1,
                                minNeighbors=5,
                                minSize=(30, 30),
                                flags=cv2.CASCADE_SCALE_IMAGE)
                    x1=-1
                    y1=-1
                    w1=0
                    h1=0
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        face_detected=True
                        if (h>h1) and (w>w1): #get the larger box
                            x1=x
                            y1=y
                            h1=h
                            w1=w
                    
                    cv2.imshow('face', img)
                    
                    if auto and face_detected and (time.time()-last_time)>2: # wait  seconds before adjusting again
                        #print("AUTO CONTROL")
                        height, width = img.shape[:2]
                        if x1>0 and y1>0:
                            print (x1,h1)
                            print(w1,h1)
                            if(x1+ w1+ margin) < width/2.0:  # left side, counter-clockwise
                                print('auto counter-clockwise')
                                drone.counter_clockwise(speed2)
                                last_time=time.time()
                            elif (x1 - margin) > width/2.0: # right side, clockwise
                                print('auto clockwise')
                                drone.clockwise(speed2)
                                last_time=time.time()
                            
                            if(w1*h1+1000 < target_area):
                                print('auto forward') # forward
                                drone.forward(speed2)
                                last_time=time.time()
                            elif(w1*h1-1000 > target_area):
                                print('auto backward') # backward
                                drone.backward(speed2)
                                last_time=time.time()
                            
                            if(y1+h1+margin<height/2.0): # up
                                print('auto up')
                                drone.up(speed2)
                                last_time=time.time()
                            elif (y1-margin>height/2.0): # down
                                print('auto down')
                                drone.down(speed2+10)
                                last_time=time.time()
                            #else: 
                            #    drone.take_picture()
                            #    last_time=time.time()
                                   


                else:
                    img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                    cv2.imshow('Original', img)
                    cv2.imshow('Canny', cv2.Canny(img, 100, 200))
                
                frame_skip = int((time.time() - start_time)/frame.time_base)
            
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        print('end program')
        drone.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
