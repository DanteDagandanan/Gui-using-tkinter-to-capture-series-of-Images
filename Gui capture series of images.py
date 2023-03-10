import tkinter as tk
import cv2
import os
from PIL import Image, ImageTk

class App:
    def __init__(self, window, window_title, video_source=0, save_directory=None):
        self.window = window
        window.resizable(False, False)
        self.window.title(window_title)
        self.video_source = video_source
        self.save_directory = save_directory
        self.captured_images = []  # list to store the captured images

        # Open the video source (in this case, the webcam)
        # Open the video source (in this case, the webcam)
        self.cap = cv2.VideoCapture(self.video_source)
    
        # Create a frame to hold the canvas and list of images
        self.frame_leftside = tk.Frame(self.window, background="gray")
        self.frame_leftside.pack(side=tk.TOP)
        
        self.frame_bottom=tk.Frame(self.window, background="blue")
        self.frame_bottom.pack(side=tk.BOTTOM)
    
        self.frame_rightside=tk.Frame(self.window, background="green")
        self.frame_rightside.pack(side=tk.RIGHT)
    
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(self.frame_leftside, width=self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack(side=tk.LEFT)
    
        # Create a frame to hold the list of images
        self.image_list_frame = tk.Frame(self.frame_leftside)
        self.image_list_frame.pack(side=tk.LEFT)
    
        # Create a vertical scrollbar for the list of images
        self.scrollbar = tk.Scrollbar(self.image_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Create a listbox to display the captured images
        self.image_list = tk.Listbox(self.image_list_frame, yscrollcommand=self.scrollbar.set)
        self.image_list.config(width=30, height=20)
        self.image_list.pack(side=tk.RIGHT, fill=tk.BOTH)
    
        # Set the scrollbar's command to scroll the listbox
        self.scrollbar.config(command=self.image_list.yview)
        
        # Load the list of captured images from the save directory
        self.load_captured_images()


        # Create a frame to hold the button and entry field
        self.control_frame = tk.Frame(self.frame_bottom)
        self.control_frame.pack(side=tk.TOP)

        # Entry field for the file name
        self.file_name_entry = tk.Entry(self.control_frame)
        self.file_name_entry.pack(side=tk.TOP, anchor=tk.CENTER, expand=True)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(self.control_frame, text="Capture Image", width=50, command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT, anchor=tk.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.angle = 0
        self.update()
        
        # Set the listbox's command to display the delete and open buttons for the selected image
        self.image_list.bind("<<ListboxSelect>>", self.display_image_controls)

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.cap.read()

        if ret:
            # Save the frame to a file
            file_name = self.file_name_entry.get()
            if file_name == "":
                file_name = "captured_image"
            filename = f"{file_name}Sample_RGB_images_{self.angle}degree.png"
            if self.save_directory is not None:
                # If a save directory is specified, use it
                filename = os.path.join(self.save_directory, filename)
            cv2.imwrite(filename, frame)

            # Increment the angle
            self.angle += 5
            if self.angle > 360:
                self.angle = 0

            # Add the image to the list of captured images
            fileName=os.path.basename(filename)
            self.captured_images.append(fileName)
            self.image_list.insert(tk.END, fileName)
            self.image_list.yview(tk.END)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)
        
    def load_captured_images(self):
        # Get a list of all files in the save directory
        file_list = os.listdir(self.save_directory)
    
        # Sort the list of files in reverse order by modification time
        file_list.sort(key=lambda x: os.path.getmtime(os.path.join(self.save_directory, x)), reverse=True)
    
        # Add the file names to the listbox widget
        for file in file_list:
            # Get the file name from the full file path
            file_name = os.path.basename(file)
            self.image_list.insert(tk.END, file_name)
            # Clear the listbox
            self.image_list.delete(0, tk.END)
            # Clear the list of captured images
            self.captured_images.clear()
            
            # Load the list of captured images from the save directory
            for file in os.listdir(self.save_directory):
                if file.endswith(".png"):
                    self.captured_images.append(os.path.join(self.save_directory, file))
            for image_file in self.captured_images:
                # Get the file name without the path
                file_name = os.path.basename(image_file)
                self.image_list.insert(tk.END, file_name)
    
    def display_image_controls(self, event):
        # Clear the previous controls
        if hasattr(self, "image_control_frame"):
            self.image_control_frame.destroy()
    
        # Get the selected image file
        image_file = self.image_list.get(self.image_list.curselection()[0])
    
        # Create a frame to hold the delete and open buttons
        self.image_control_frame = tk.Frame(self.image_list_frame)
        self.image_control_frame.pack(side=tk.TOP)
    
        # Create the delete button
        self.btn_delete_image = tk.Button(self.image_control_frame, text="Delete", command=lambda: self.delete_image(image_file))
        self.btn_delete_image.pack(side=tk.BOTTOM)
    
        # Create the open button
        self.btn_open_image = tk.Button(self.image_control_frame, text="Open", command=lambda: self.open_image(image_file))
        self.btn_open_image.pack(side=tk.BOTTOM)

        
    def delete_image(self, image_file):
        if os.path.exists(image_file):
            os.remove(image_file)
            self.image_list.delete(self.image_list.curselection())
            self.captured_images.remove(image_file)

        
    def open_image(self, image_file):
        # Open the image file using the default image viewer
        os.startfile(image_file)

# Create a new Tkinter window
window = tk.Tk()

# Create an instance of the App class, passing in the window and a title for the window
# Set the save_directory argument to specify a directory to save the captured images
app = App(window, "Webcam Image Capture", save_directory="C:/Users/PRO/Desktop/zip/NIR/NIR code/sparkkkkk/")

