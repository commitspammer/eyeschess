import cv2 as cv
import numpy as np
from time import time

def show(name, img):
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.imshow(name, img)

def crop(img, edges):
    edgesbyx = sorted(edges, key=lambda e: e[0])
    edgesbyy = sorted(edges, key=lambda e: e[1])
    minx, _, _, maxx = [e[0] for e in edgesbyx]
    miny, _, _, maxy = [e[1] for e in edgesbyy]
    x1, y1 = maxx - minx, maxy - miny
    projections = [(0,0), (x1,0), (0,y1), (x1,y1)]
    homography_m = cv.getPerspectiveTransform(np.float32(edges), np.float32(projections))
    cropped = cv.warpPerspective(img, homography_m, (x1, y1))
    return cropped

# processing is so powerful that it slows down the video
def run(emitVideo, emitCrop, emitBaseFrame, emitDifference, emitMove):
    vcap = cv.VideoCapture('./input/top.mp4')
    if not vcap.isOpened():
        print('file cannot be opened')

    frame = None
    baseFrame = None
    edges = []
    cropped = None
    baseCropped = None

    def on_click(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONUP:
            if len(edges) < 4:
                edges.append((x, y))
                print(edges)
        if event == cv.EVENT_MBUTTONUP:
            edges.clear()
            print(edges)
    cv.namedWindow('Select edges h1->h8->a1->a8', cv.WINDOW_NORMAL)
    cv.setMouseCallback('Select edges h1->h8->a1->a8', on_click)

    start = time()
    while True:
        _, frame = vcap.read()
        if frame is not None:
            cv.waitKey(4) # delay is needed for video files
            cv.imshow('Select edges h1->h8->a1->a8', frame)
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            emitVideo(frame)
            if len(edges) == 4:
                if baseFrame is not None:
                    cropped = crop(frame, edges)
                    emitCrop(cropped)
                    baseCropped = crop(baseFrame, edges)
                    emitBaseFrame(baseCropped)
                    diff = cv.absdiff(baseCropped, cropped)
                    _, diff = cv.threshold(diff, 30, 255, cv.THRESH_BINARY)
                    emitDifference(diff)
                    height, width = diff.shape
                    weight = np.sum(diff[0:height-1, 0:width-1]) / (height * width) # this ranges 0..255 wtf?
                    print(f'weight={weight}')
                    if weight > 1.5 and weight < 8: # should be: (height * width * (3/4)) / 64
                        if time() - start > 2.25:
                            densities = np.zeros((8,8), dtype=int)
                            for i in range(height):
                                for j in range(width):
                                    densities[int(8*i/height), int(8*j/width)] += diff[i, j]
                            square1 = np.unravel_index(np.argmax(densities, axis=None), densities.shape)
                            densities[square1[0], square1[1]] = 0
                            square2 = np.unravel_index(np.argmax(densities, axis=None), densities.shape)
                            print(square1, square2)
                            move = cv.cvtColor(diff, cv.COLOR_GRAY2BGR)
                            cv.rectangle(move,
                                ( int(square1[1]*width/8), int(square1[0]*height/8) ),
                                ( int((square1[1]+1)*width/8), int((square1[0]+1)*height/8) ),
                                (0,0,255),3)
                            cv.rectangle(move,
                                ( int(square2[1]*width/8), int(square2[0]*height/8) ),
                                ( int((square2[1]+1)*width/8), int((square2[0]+1)*height/8) ),
                                (0,0,255),3)
                            emitMove(move)
                            baseFrame = frame.copy()
                            start = time()
                    else:
                        start = time()
                else:
                    baseFrame = frame.copy()
            else:
                pass
        else:
            print('no frame')
            break
    vcap.release()
    cv.destroyAllWindows()
    print('video stop')
