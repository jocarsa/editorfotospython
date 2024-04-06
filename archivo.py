import os
from PIL import Image, ImageTk, ExifTags, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

class ImageDisplayApp:
    def __init__(self):
        self.folder_path = None
        self.destination_folder = None
        self.image_list = []
        self.current_index = 0
        self.current_image_path = None
        
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.bind("<Right>", self.show_next_image)
        self.root.bind("<Left>", self.show_previous_image)
        self.root.bind("z", self.copy_image)
        
        self.label = tk.Label(self.root)
        self.label.pack()
        
        self.create_menu()  # Call the create_menu() method
        
        self.root.mainloop()
    
    def create_menu(self):
        print("menu")
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Origin Folder", command=self.set_origin_folder)
        file_menu.add_command(label="Set Destination Folder", command=self.set_destination_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_credits)
        menubar.add_cascade(label="Help", menu=help_menu)
    
    def set_origin_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.load_images()
            self.show_image(self.current_index)
    
    def set_destination_folder(self):
        destination_folder = filedialog.askdirectory()
        if destination_folder:
            self.destination_folder = destination_folder
    
    def show_credits(self):
        messagebox.showinfo("About", "Image Viewer\nVersion 1.0\nDeveloped by Your Name")
    
    def load_images(self):
        if self.folder_path:
            files = os.listdir(self.folder_path)
            self.image_list = sorted([os.path.join(self.folder_path, f) for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    
    def show_image(self, index):
        if self.image_list:
            image_path = self.image_list[index]
            image = Image.open(image_path)
            image = self.rotate_image(image)
            
            window_height = self.root.winfo_screenheight() - 100  # Adjust 100 as needed for window decorations
            width, height = image.size
            aspect_ratio = width / height
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)  # Resampling filter
            
            self.tk_image = ImageTk.PhotoImage(image)
            self.label.config(image=self.tk_image)
            
            self.current_image_path = image_path  # Update current_image_path
            
            # Update window title
            self.update_window_title()
    
    def update_window_title(self):
        if self.current_image_path:  # Check if current_image_path is not None
            current_image_name = os.path.basename(self.current_image_path)
            total_images = len(self.image_list)
            progress = f"{self.current_index + 1} of {total_images} ({(self.current_index + 1) / total_images * 100:.2f}%)"
            self.root.title(f"Image Viewer - {current_image_name} - {progress}")
        else:
            self.root.title("Image Viewer")
    
    def rotate_image(self, image):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())

            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        
        return image
    
    def show_next_image(self, event):
        if self.image_list:
            self.current_index = (self.current_index + 1) % len(self.image_list)
            self.show_image(self.current_index)
    
    def show_previous_image(self, event):
        if self.image_list:
            self.current_index = (self.current_index - 1) % len(self.image_list)
            self.show_image(self.current_index)
    
    def copy_image(self, event):
        if hasattr(self, 'current_image_path') and self.destination_folder:
            image_path = self.current_image_path
            image = Image.open(image_path)
            try:
                exif = image._getexif()
                date_time_original = exif[36867]  # EXIF tag for DateTimeOriginal
                new_name = date_time_original.replace(':', '-').replace(' ', '-') + '.jpg'
            except (KeyError, AttributeError, TypeError):
                # If EXIF data doesn't exist or doesn't contain the required tag
                new_name = "unnamed.jpg"
            
            destination_path = os.path.join(self.destination_folder, new_name)
            shutil.copy(image_path, destination_path)
            
            # Save the copied image with original orientation and EXIF data
            copied_image = Image.open(destination_path)
            copied_image = ImageOps.autocontrast(copied_image)
            copied_image.save(destination_path, exif=copied_image.info.get('exif'))
            
            print(f"Image copied to {destination_path} and renamed to {new_name}")

# Create and run the application
app = ImageDisplayApp()
