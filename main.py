import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw,ImageFont
import torch
import cv2

class ImagePreviewer:
    def __init__(self, root):
        #Define GUI elements
        self.root = root
        self.root.title("Image Previewer")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True) 

        self.scrollbar = tk.Scrollbar(self.frame)  
        self.scrollbar.pack(side="right", fill="y") 

        self.listbox = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.listbox.yview) 

        self.listbox.bind('<<ListboxSelect>>', self.load_image)

        self.canvas1 = tk.Canvas(self.frame, width=500, height=500)
        self.canvas1.pack(side="right", fill="both", expand=True) 

        self.canvas2 = tk.Canvas(self.frame, width=500, height=500)
        self.canvas2.pack(side="right", fill="both", expand=True) 

        self.button = tk.Button(self.root, text="Open Folder", command=self.open_folder)
        self.button.pack()

        self.button_yolo = tk.Button(self.root, text="Apply YOLO", command=self.apply_yolo)
        self.button_yolo.pack()

        self. model = torch.hub.load('ultralytics/yolov5', 'custom', path='/Users/wagnertamas/PycharmProjects/YOLOv5-Vehicle-Detection/weights/best.pt', force_reload=True)

    def open_folder(self):
        #Open the folder and get the list of image files
        folder_path = filedialog.askdirectory()
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.PNG') or f.endswith('.JPG')]

        image_files.sort()

        self.listbox.delete(0, tk.END)
        for image_file in image_files:
            self.listbox.insert(tk.END, os.path.join(folder_path, image_file))

    def load_image(self, evt):
        # Get the path of the selected image
        self.file_path = self.listbox.get(self.listbox.curselection())
        image = Image.open(self.file_path)

        # Calculate the aspect ratio
        aspect_ratio = image.width / image.height

        # Get the current window size
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Calculate new dimensions based on the window size
        new_width = window_width // 2  # Divide by 2 because there are two images
        new_height = round(new_width / aspect_ratio)

        # Ensure the new height does not exceed the window height
        new_height = min(new_height, window_height)

        # Recalculate the width based on the new height
        new_width = round(new_height * aspect_ratio)

        image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convert the image to a PhotoImage and add it to the canvas
        self.imageTk1 = ImageTk.PhotoImage(image)
        self.canvas1.create_image(0, 0, anchor="nw", image=self.imageTk1)

        self.imageTk2 = ImageTk.PhotoImage(image)
        self.canvas2.create_image(0, 0, anchor="nw", image=self.imageTk2)

    def apply_yolo(self):
        # Call your YOLO function here. The function should return the path of the output image.
        predict_image = self.model(self.file_path).pandas().xyxyn[0]
        # Load the output image and display it on the right canvas
        output_image = Image.open(self.file_path)
        draw = ImageDraw.Draw(output_image)
        for _, row in predict_image.iterrows():
            xmin = row['xmin'] * output_image.width
            ymin = row['ymin'] * output_image.height
            xmax = row['xmax'] * output_image.width
            ymax = row['ymax'] * output_image.height
            draw.rectangle((xmin, ymin,xmax, ymax), outline="red", width=5)

            # Draw category and confidence
            category = row['name']
            confidence = row['confidence']
            text = f"{category} {confidence:0.2f}"
            draw.text((xmin, ymin-20), text, fill="red", font=ImageFont.truetype("Arial.ttf",26))

        # Calculate the aspect ratio of the output image
        aspect_ratio = output_image.width / output_image.height

        # Get the current width and height of the window
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Calculate the new width and height of the image
        new_width = window_width // 2
        new_height = round(new_width / aspect_ratio)

        # Ensure that the new height is not greater than the window height
        new_height = min(new_height, window_height)

        # Calculate the new width and height of the image
        new_width = round(new_height * aspect_ratio)

        # Resize the image and convert it to a PhotoImage
        output_image = output_image.resize((new_width, new_height), Image.LANCZOS)
        self.imageTk2 = ImageTk.PhotoImage(output_image)

        # Draw the output image on the canvas
        self.canvas2.create_image(0, 0, anchor="nw", image=self.imageTk2)
        

        

root = tk.Tk()
app = ImagePreviewer(root)
root.mainloop()