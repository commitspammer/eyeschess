import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import processor
import cv2 as cv
from threading import Thread
import requests

window = tk.Tk()
window.title('EyesChess')

#url = 'https://cataas.com/cat/cute/says/LOADING...?fontSize=100&fontColor=white&width=400&height=400'
url = 'https://picsum.photos/id/400/400'
cat = ImageTk.PhotoImage(Image.open(requests.get(url, stream=True).raw))
url = 'https://fen2image.chessvision.ai/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
fen = ImageTk.PhotoImage(Image.open(requests.get(url, stream=True).raw).resize((400,400)))
video      = ttk.Label(master=window, image=cat)
crop       = ttk.Label(master=window, image=cat)
difference = ttk.Label(master=window, image=cat)
baseFrame  = ttk.Label(master=window, image=cat)
move       = ttk.Label(master=window, image=cat)
board      = ttk.Label(master=window, image=fen)
video      .grid(row=0, column=0, padx=0, pady=0)
crop       .grid(row=0, column=1, padx=0, pady=0)
difference .grid(row=0, column=2, padx=0, pady=0)
baseFrame  .grid(row=1, column=0, padx=0, pady=0)
move       .grid(row=1, column=1, padx=0, pady=0)
board      .grid(row=1, column=2, padx=0, pady=0)

def matToImage(mat):
    try:
        b, g, r = cv.split(mat) 
        mat = cv.merge((r, g, b)) 
    finally:
        img = Image.fromarray(mat)
        return img

def onChange(label):
    def display(frame):
        im = matToImage(frame)
        img = im.resize((400, 400), Image.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(img)
        label.configure(image=imgtk)
        label.image = imgtk
    return display

t = Thread(target=processor.run, args=(
    onChange(video), onChange(crop), onChange(baseFrame), onChange(difference), onChange(move)
))
t.start()
window.mainloop()
