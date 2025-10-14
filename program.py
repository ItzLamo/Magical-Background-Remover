import os
import threading
from rembg import remove  # type: ignore
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magical Background Remover")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        self.root.minsize(900, 700)
        
        self.colors = {
            'primary': '#3b82f6',
            'secondary': '#8b5cf6',
            'success': '#10b981',
            'danger': '#ef4444',
            'dark': '#1f2937',
            'light': '#f9fafb',
            'border': '#e5e7eb'
        }

        self.input_image_path = None
        self.output_image_path = None
        self.output_image = None
        self.original_output = None
        self.history = []
        
        self.zoom_level = 1.0
        self.is_processing = False
        
        self.setup_style()
        self.create_widgets()
        self.setup_keyboard_shortcuts()

    # ----------------- STYLE SETUP -------------------------
    
    def setup_style(self):
        """Configure ttk styles for a modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Primary.TButton', background=self.colors['primary'], 
                       foreground='white', font=('Arial', 10, 'bold'), 
                       borderwidth=0, padding=10)
        style.map('Primary.TButton', background=[('active', '#2563eb')])
        
        style.configure('Success.TButton', background=self.colors['success'], 
                       foreground='white', font=('Arial', 10, 'bold'), 
                       borderwidth=0, padding=10)
        style.map('Success.TButton', background=[('active', '#059669')])
        
    # --------------------- UI SETUP -------------------
    
    def create_widgets(self):
        header = tk.Label(self.root, text="Magical Background Remover",
                          font=("Arial", 26, "bold"), fg=self.colors['primary'], 
                          bg=self.colors['light'])
        header.pack(pady=15, fill=tk.X)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=300)
        self.progress.pack(pady=5)
        self.progress.pack_forget()
        
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 10), 
                                     fg=self.colors['dark'])
        self.status_label.pack()

        frame = ttk.Frame(self.root)
        frame.pack(pady=10, padx=20, expand=True, fill=tk.BOTH)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        input_frame = ttk.Frame(frame)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(input_frame, text="Original Image", 
                font=("Arial", 14, "bold"), fg=self.colors['dark']).pack()
        
        self.input_canvas = tk.Canvas(input_frame, bg=self.colors['light'], 
                                      relief="solid", bd=2, highlightthickness=0)
        self.input_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.input_canvas.config(width=400, height=400)
        
        self.input_canvas.create_text(200, 200, text="Drag & Drop Image Here\nor Click Upload", 
                                      font=("Arial", 12), fill="#888", tags="placeholder")

        output_frame = ttk.Frame(frame)
        output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(output_frame, text="✨ Processed Image", 
                font=("Arial", 14, "bold"), fg=self.colors['dark']).pack()
        
        self.output_canvas = tk.Canvas(output_frame, bg=self.colors['light'], 
                                       relief="solid", bd=2, highlightthickness=0)
        self.output_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.output_canvas.config(width=400, height=400)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Upload Image", 
                  command=self.upload_image, style='Primary.TButton').grid(row=0, column=0, padx=5)
        
        self.remove_bg_button = ttk.Button(button_frame, text="Remove Background", 
                                          command=self.remove_background_threaded, 
                                          state=tk.DISABLED, style='Primary.TButton')
        self.remove_bg_button.grid(row=0, column=1, padx=5)
        
        self.batch_button = ttk.Button(button_frame, text="Batch Process", 
                                      command=self.batch_process, 
                                      style='Primary.TButton')
        self.batch_button.grid(row=0, column=2, padx=5)

        effects_frame = ttk.LabelFrame(self.root, text="Effects & Tools", padding=10)
        effects_frame.pack(pady=10, padx=20, fill=tk.X)

        self.magic_button = ttk.Button(effects_frame, text="Magic Touch", 
                                       command=self.magic_touch, state=tk.DISABLED)
        self.magic_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.blur_button = ttk.Button(effects_frame, text="Blur Effect", 
                                      command=self.apply_blur, state=tk.DISABLED)
        self.blur_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.sharpen_button = ttk.Button(effects_frame, text="Sharpen", 
                                         command=self.apply_sharpen, state=tk.DISABLED)
        self.sharpen_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.grayscale_button = ttk.Button(effects_frame, text="Grayscale", 
                                          command=self.apply_grayscale, state=tk.DISABLED)
        self.grayscale_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.replace_color_button = ttk.Button(effects_frame, text="Replace BG Color", 
                                              command=self.replace_bg_color, state=tk.DISABLED)
        self.replace_color_button.grid(row=0, column=5, padx=5, pady=5)
        
        self.replace_img_button = ttk.Button(effects_frame, text="🖼️ Replace BG Image", 
                                            command=self.replace_bg_image, state=tk.DISABLED)
        self.replace_img_button.grid(row=0, column=6, padx=5, pady=5)
        
        self.undo_button = ttk.Button(effects_frame, text="↶ Undo", 
                                     command=self.undo, state=tk.DISABLED)
        self.undo_button.grid(row=0, column=7, padx=7, pady=5)
        
        save_frame = ttk.Frame(self.root)
        save_frame.pack(pady=10)
        
        self.save_button = ttk.Button(save_frame, text="Save Output", 
                                     command=self.save_output, 
                                     state=tk.DISABLED, style='Success.TButton')
        self.save_button.grid(row=0, column=8, padx=5)
        
        tk.Label(save_frame, text="Format:").grid(row=0, column=1, padx=5)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(save_frame, textvariable=self.format_var, 
                                   values=["PNG", "JPEG", "WEBP", "BMP"], 
                                   state="readonly", width=8)
        format_combo.grid(row=0, column=2, padx=5)

        footer = tk.Label(self.root, text="Developed by Hassan Ahmed for Hack Club | Press F1 for Help", 
                         fg="#888", font=("Arial", 9), bg=self.colors['light'])
        footer.pack(side="bottom", pady=8, fill=tk.X)
        
        self.setup_drag_drop()

    # ---------------------------- SETUP FUNCTIONS ----------------------
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.upload_image())
        self.root.bind('<Control-s>', lambda e: self.save_output() if self.output_image_path else None)
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            self.input_canvas.drop_target_register(DND_FILES)
            self.input_canvas.dnd_bind('<<Drop>>', self.drop_image)
        except:
            pass
    
    def drop_image(self, event):
        """Handle dropped files"""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.load_input_image(files[0])
    
    # -------------------------- IMAGE FUNCTIONS ---------------------

    def upload_image(self):
        """Upload an image file"""
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp;*.gif")]
        )
        if not path:
            return
        self.load_input_image(path)

    def load_input_image(self, path):
        """Load and display input image"""
        try:
            self.input_image_path = path
            img = Image.open(path)
            
            self.original_size = img.size
            
            img_display = img.copy()
            img_display.thumbnail((300, 300), Image.Resampling.LANCZOS)
            self.input_image = ImageTk.PhotoImage(img_display)
            self.input_canvas.delete("all")
            
            canvas_width = self.input_canvas.winfo_width() or 400
            canvas_height = self.input_canvas.winfo_height() or 400
            x = canvas_width // 2
            y = canvas_height // 2
            self.input_canvas.create_image(x, y, image=self.input_image)
            
            self.remove_bg_button.config(state=tk.NORMAL)
            self.magic_button.config(state=tk.NORMAL)
            self.update_status(f"Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.update_status("Error loading image")

    def remove_background_threaded(self):
        """Remove background in a separate thread to prevent UI freezing"""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current operation to complete")
            return
        
        thread = threading.Thread(target=self.remove_background)
        thread.daemon = True
        thread.start()
    
    def remove_background(self):
        """Remove background from the image"""
        try:
            self.is_processing = True
            self.update_status("Removing background...")
            self.show_progress()
            
            with open(self.input_image_path, 'rb') as f:
                output_data = remove(f.read())
            
            self.output_image_path = "temp_output.png"
            with open(self.output_image_path, 'wb') as out:
                out.write(output_data)
            
            img = Image.open(self.output_image_path)
            self.save_to_history(img)
            self.display_output(img)
            
            self.root.after(0, lambda: self.enable_effect_buttons())
            self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))
            
            self.hide_progress()
            self.update_status("Background removed successfully!")
            self.root.after(0, lambda: messagebox.showinfo("Success", "Background removed successfully!"))
        except Exception as e:
            self.hide_progress()
            self.update_status("Error removing background")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed: {e}"))
        finally:
            self.is_processing = False

    def display_output(self, img):
        """Display output image on canvas"""
        self.original_output = img.copy()
        
        img_display = img.copy()
        img_display.thumbnail((400, 400), Image.Resampling.LANCZOS)
        self.output_image = ImageTk.PhotoImage(img_display)
        
        self.output_canvas.delete("all")
        canvas_width = self.output_canvas.winfo_width() or 400
        canvas_height = self.output_canvas.winfo_height() or 400
        x = canvas_width // 2
        y = canvas_height // 2
        self.output_canvas.create_image(x, y, image=self.output_image)

    # -------------------------- EFFECT FUNCTIONS ---------------------
    
    def magic_touch(self):
        """Apply magical enhancement effect"""
        if not self.input_image_path:
            messagebox.showwarning("Warning", "Upload an image first!")
            return
        try:
            self.update_status("Applying magic touch...")
            
            with open(self.input_image_path, 'rb') as f:
                output_data = remove(f.read())
            
            with open("magic_temp.png", 'wb') as out:
                out.write(output_data)
            
            img = Image.open("magic_temp.png").convert("RGBA")
            
            img = ImageEnhance.Brightness(img).enhance(1.2)
            img = ImageEnhance.Contrast(img).enhance(1.3)
            img = ImageEnhance.Sharpness(img).enhance(1.5)

            gradient = Image.new("RGBA", img.size, "#ffffff")
            for y in range(img.height):
                r = int(255 - (y / img.height) * 40)
                g = int(255 - (y / img.height) * 60)
                b = int(255 - (y / img.height) * 80)
                for x in range(img.width):
                    gradient.putpixel((x, y), (r, g, b, 255))

            gradient.paste(img, (0, 0), img)
            
            self.save_to_history(gradient)
            self.display_output(gradient)
            self.save_button.config(state=tk.NORMAL)
            self.enable_effect_buttons()
            
            if os.path.exists("magic_temp.png"):
                os.remove("magic_temp.png")
                
            self.update_status("Magic applied!")
            messagebox.showinfo("Magic Complete!", "Your image has been magically enhanced!")

        except Exception as e:
            messagebox.showerror("Error", f"Magic failed: {e}")
            self.update_status("Magic failed")
    
    def apply_blur(self):
        """Apply blur effect"""
        if not self.original_output:
            messagebox.showwarning("Warning", "Process an image first!")
            return
        try:
            img = self.original_output.copy()
            img = img.filter(ImageFilter.GaussianBlur(radius=5))
            self.save_to_history(img)
            self.display_output(img)
            self.update_status("Blur effect applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply blur: {e}")
    
    def apply_sharpen(self):
        """Apply sharpen effect"""
        if not self.original_output:
            messagebox.showwarning("Warning", "Process an image first!")
            return
        try:
            img = self.original_output.copy()
            img = img.filter(ImageFilter.SHARPEN)
            self.save_to_history(img)
            self.display_output(img)
            self.update_status("Sharpen effect applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply sharpen: {e}")
    
    def apply_grayscale(self):
        """Apply grayscale effect"""
        if not self.original_output:
            messagebox.showwarning("Warning", "Process an image first!")
            return
        try:
            img = self.original_output.copy()
            img = ImageOps.grayscale(img).convert("RGBA")
            self.save_to_history(img)
            self.display_output(img)
            self.update_status("Grayscale effect applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply grayscale: {e}")

    def replace_bg_color(self):
        """Replace background with solid color"""
        if not self.output_image_path:
            messagebox.showwarning("Warning", "Remove the background first!")
            return
        color = colorchooser.askcolor(title="Pick a background color")[1]
        if not color:
            return
        try:
            img = Image.open(self.output_image_path).convert("RGBA")
            bg = Image.new("RGBA", img.size, color)
            bg.paste(img, (0, 0), img)
            self.save_to_history(bg)
            self.display_output(bg)
            self.update_status(f"Background replaced with {color}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to replace background: {e}")

    def replace_bg_image(self):
        """Replace background with another image"""
        if not self.output_image_path:
            messagebox.showwarning("Warning", "Remove the background first!")
            return
        bg_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if not bg_path:
            return
        try:
            img = Image.open(self.output_image_path).convert("RGBA")
            bg = Image.open(bg_path).convert("RGBA").resize(img.size, Image.Resampling.LANCZOS)
            bg.paste(img, (0, 0), img)
            self.save_to_history(bg)
            self.display_output(bg)
            self.update_status("Background replaced with image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to replace background: {e}")
    
    # -------------------------- BATCH PROCESSING ---------------------
    
    def batch_process(self):
        """Process multiple images at once"""
        paths = filedialog.askopenfilenames(
            title="Select Images to Process",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if not paths:
            return
        
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return
        
        self.update_status(f"Processing {len(paths)} images...")
        self.show_progress()
        
        def batch_worker():
            try:
                for i, path in enumerate(paths):
                    with open(path, 'rb') as f:
                        output_data = remove(f.read())
                    
                    filename = os.path.splitext(os.path.basename(path))[0]
                    output_path = os.path.join(output_dir, f"{filename}_nobg.png")
                    
                    with open(output_path, 'wb') as out:
                        out.write(output_data)
                    
                    self.root.after(0, lambda i=i: self.update_status(
                        f"Processed {i+1}/{len(paths)} images"))
                
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: self.update_status(
                    f"Batch processing complete! Saved to {output_dir}"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Processed {len(paths)} images successfully!"))
            except Exception as e:
                self.root.after(0, lambda: self.hide_progress())
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Batch processing failed: {e}"))
        
        thread = threading.Thread(target=batch_worker)
        thread.daemon = True
        thread.start()
    
    # -------------------------- FUNCTIONS ---------------------
    
    def save_to_history(self, img):
        """Save current state to history for undo"""
        self.history.append(self.original_output.copy() if self.original_output else None)
        if len(self.history) > 10:  # Keep only last 10 states
            self.history.pop(0)
        self.undo_button.config(state=tk.NORMAL)
    
    def undo(self):
        """Undo last operation"""
        if not self.history:
            messagebox.showinfo("Info", "Nothing to undo")
            return
        
        previous_state = self.history.pop()
        if previous_state:
            self.display_output(previous_state)
            self.update_status("Undo successful")
        
        if not self.history:
            self.undo_button.config(state=tk.DISABLED)
    
    def enable_effect_buttons(self):
        """Enable all effect buttons"""
        self.magic_button.config(state=tk.NORMAL)
        self.blur_button.config(state=tk.NORMAL)
        self.sharpen_button.config(state=tk.NORMAL)
        self.grayscale_button.config(state=tk.NORMAL)
        self.replace_color_button.config(state=tk.NORMAL)
        self.replace_img_button.config(state=tk.NORMAL)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def show_progress(self):
        """Show progress bar"""
        self.progress.pack(before=self.status_label, pady=5)
        self.progress.start(10)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress.stop()
        self.progress.pack_forget()
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
    Magical Background Remover - Help

Keyboard Shortcuts:
    • Ctrl+O: Upload Image
    • Ctrl+S: Save Output
    • Ctrl+Z: Undo
    • F1: Show Help
    • ESC: Exit

Features:
    • Drag & Drop: Drag images directly onto the input area
    • Remove Background: AI-powered background removal
    • Magic Touch: Auto-enhance with gradient background
    • Effects: Blur, Sharpen, Grayscale
    • Replace BG: Use solid color or custom image
    • Batch Process: Process multiple images at once

Supported Formats:
    • Input: PNG, JPEG, BMP, WEBP, GIF
    • Output: PNG, JPEG, WEBP, BMP
        """
        messagebox.showinfo("Help", help_text)

    def save_output(self):
        """Save the output image"""
        if not self.original_output:
            messagebox.showwarning("Warning", "No output to save!")
            return
        
        file_format = self.format_var.get()
        ext = file_format.lower()
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[
                (f"{file_format} Files", f"*.{ext}"),
                ("All Files", "*.*")
            ]
        )
        if not save_path:
            return
        
        try:
            img = self.original_output.copy()
            
            if file_format == "JPEG" and img.mode == "RGBA":
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            img.save(save_path, file_format)
            self.update_status(f"Saved to {os.path.basename(save_path)}")
            messagebox.showinfo("Saved", f"Saved successfully to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    try:
        root = TkinterDnD.Tk()
    except:
        root = tk.Tk()
    
    app = BackgroundRemoverApp(root)
    root.mainloop()