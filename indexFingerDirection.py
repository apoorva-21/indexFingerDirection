'''
OpenCV program to detect the finger of the hand that is outstretched furthest away from the palm::
    -press 'b' with the 'frame' window active to begin background subtraction, and subsequent tracking within the bounding box (CYAN Square)
'''



import cv2
import numpy as np
from imutils.video import WebcamVideoStream

loYCRCB = (0,138,101)
hiYCRCB = (198,155,148)
cap = WebcamVideoStream(src = 0).start()
bgCap = False
rx1,rx2,ry1,ry2 = 0,400,0,400
font = cv2.FONT_HERSHEY_SIMPLEX

def FindDistance(A,B): 
 return np.sqrt(np.power((np.absolute(A[0]-B[0])),2) + np.power(np.absolute((A[1]-B[1])),2)) 
 

def putText(frame, txt):
    frame = cv2.putText(frame,'Fingers:'+str(txt),(0,70),font,1,(255,255,255),cv2.CV_AA)
    return frame
while True:
    frame = cap.read()
    frame = cv2.flip(frame,1)
    frame = cv2.GaussianBlur(frame, (0,0), 2)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break
    if k == ord('b'):
        bg = frame.copy()
        bgCap = True
        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2YCR_CB)
        maskBG = cv2.inRange(bg,loYCRCB,hiYCRCB)
    if bgCap:
        frame = cv2.rectangle(frame, (rx1,ry1), (rx2,ry2), (255,255,0),2)
        frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
        mask = cv2.inRange(frame2,loYCRCB, hiYCRCB)
        res = (mask - maskBG)
        cv2.imshow('res', res)
        disTrans = cv2.distanceTransform(res, cv2.DIST_L2, 5)
        cv2.imshow('disTrans',disTrans)
        frame2 = cv2.bitwise_and(frame2, frame2, mask = res)
        frame2 = cv2.cvtColor(frame2, cv2.COLOR_YCR_CB2BGR)
        img, cnts, hierarchy = cv2.findContours(res[ry1:ry2,rx1:rx2], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        c = 0
        if(len(cnts) > 0):
            maxArea = cv2.contourArea(cnts[0])
            for i in range(1, len(cnts)):
                area = cv2.contourArea(cnts[i])
                if area > maxArea:
                    maxArea = area
                    c = cnts[i]
            area = cv2.contourArea(c)
            cx, cy = 0, 0
            if area > 10000: 
                M = cv2.moments(c)
                if(M['m00'] != 0):
                    cx = M['m10']/M['m00']
                    cy = M['m01']/M['m00']
                centroid = (int(cx),int(cy))
                frame = cv2.circle(frame, centroid, 5,(255,0,0),-1)
                cv2.putText(frame, 'Center', tuple(centroid), font, 2, (255,255,0),2)
                if(len(c) > 0):
                    hull= cv2.convexHull(c, returnPoints = False)
                    hull2 = cv2.convexHull(c)
                    defects = cv2.convexityDefects(c,hull)
                    farDefect = []
                    finger = []
                    if(len(defects) > 0):
                        for i in range(defects.shape[0]):
                            s,e,f,d = defects[i,0]
                            start = tuple(c[s][0])
                            end = tuple(c[e][0])
                            print end
                            far = tuple(c[f][0])
                            cv2.line(frame,start,end,[0,255,0],2)

                    #get all points from contour hull, append them to the list probable fingertips::
                        finger = []
                        for i in range(0, len(hull2) - 1):
                                finger.append(hull2[i][0])
                        indexFinger = []
                        max = FindDistance(finger[0], centroid)

                        #getting the extrema in the convex Hull, furthest away from the contour centroid::
                        for i in range(1,len(finger)):
                            if (FindDistance(finger[i], centroid) > max):
                                indexFinger = finger[i]
                                max = FindDistance(finger[i], centroid)
                        indexFinger = np.array(indexFinger, np.uint16)
                        if(len(indexFinger) > 0):
                            tipAndCenterEuclidean = np.sqrt(np.power(indexFinger[0] - centroid[0], 2) + np.power(indexFinger[1] - centroid[1], 2))
                            print tipAndCenterEuclidean
                            if(tipAndCenterEuclidean < 90):
                                cv2.putText(frame,'Fist Closed',(100,100),font,2,(0,0,255),2)  
                            else:
                                if((indexFinger[0] - centroid[0]) > 60):                          
                                    cv2.putText(frame,'Right',(100,100),font,2,(0,0,255),2)
                                elif ((indexFinger[0] - centroid[0]) < -60):
                                    cv2.putText(frame,'Left',(100,100),font,2,(0,0,255),2)
                                elif((indexFinger[1] - centroid[1]) > 60):                          
                                    cv2.putText(frame,'Down',(100,100),font,2,(0,0,255),2)
                                elif((indexFinger[1] - centroid[1]) < -60):                          
                                    cv2.putText(frame,'Up',(100,100),font,2,(0,0,255),2)
                                cv2.circle(frame, tuple(indexFinger),5,(0,0,255),-1)
                        if( k == ord('h')) : 
                            print 'indexFinger:{}\t Centroid:{}'.format(indexFinger, centroid)
    cv2.imshow('frame',frame)
cv2.destroyAllWindows()
