import os
from PIL import Image, ImageTk, ExifTags, ImageOps
import tkinter as tk
import shutil

class ImageDisplayApp:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.image_list = sorted(self.load_images())  # Sort images alphabetically
        self.current_index = 0
        self.current_image_path = None
        
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.bind("<Right>", self.show_next_image)
        self.root.bind("<Left>", self.show_previous_image)
        self.root.bind("z", self.copy_image)
        
        self.label = tk.Label(self.root)
        self.label.pack()
        
        self.update_window_title()
        self.show_image(self.current_index)
        
        self.root.mainloop()
    
    def load_images(self):
        files = os.listdir(self.folder_path)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return [os.path.join(self.folder_path, f) for f in image_files]
    
    def show_image(self, index):
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
        total_images = len(self.image_list)
        if self.current_image_path:  # Check if current_image_path is not None
            current_image_name = os.path.basename(self.current_image_path)
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
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.show_image(self.current_index)
    
    def show_previous_image(self, event):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.show_image(self.current_index)
    
    def copy_image(self, event):
        if hasattr(self, 'current_image_path'):
            image_path = self.current_image_path
            image = Image.open(image_path)
            try:
                exif = image._getexif()
                date_time_original = exif[36867]  # EXIF tag for DateTimeOriginal
                new_name = date_time_original.replace(':', '-').replace(' ', '-') + '.jpg'
            except (KeyError, AttributeError, TypeError):
                # If EXIF data doesn't exist or doesn't contain the required tag
                new_name = "unnamed.jpg"
            
            destination_folder = "/Users/josevicente/Desktop/seleccion2/"
            destination_path = os.path.join(destination_folder, new_name)
            shutil.copy(image_path, destination_path)
            
            # Save the copied image with original orientation and EXIF data
            copied_image = Image.open(destination_path)
            copied_image = ImageOps.autocontrast(copied_image)
            copied_image.save(destination_path, exif=copied_image.info.get('exif'))
            
            print(f"Image copied to {destination_path} and renamed to {new_name}")

# Path to the folder containing images
folder_path = "/Users/josevicente/Desktop/Seleccion"

# Create and run the application
app = ImageDisplayApp(folder_path)
