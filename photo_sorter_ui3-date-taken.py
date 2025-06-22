# Filename: photo_sorter_ui.py
import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# Global control flags
is_paused = False
is_cancelled = False
is_quick_mode = False

# Predefined folder name formats for the dropdown
FOLDER_NAME_FORMATS = {
    "YYYY-MM": "%Y-%m",
    "Month-YYYY": "%B-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
}

# Define accepted image and video file extensions
image_video_extensions = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic',
    '.raf', '.cr2', '.rw2', '.erf', '.nrw', '.nef', '.rwz', '.dng', '.arw', '.eip', '.bay',
    '.dcr', '.gpr', '.raw', '.crw', '.3fr', '.sr2', '.k25', '.mef', '.kc2', '.cs1', '.mos',
    '.orf', '.kdc', '.cr3', '.srf', '.srw', '.j6i', '.ari', '.fff', '.mrw', '.mfw', '.rwl',
    '.x3f', '.pef', '.iiq', '.cxi', '.nksc',
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.webm'
}

def get_exif_date_taken(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None

def get_video_creation_date(file_path):
    try:
        parser = createParser(file_path)
        if not parser:
            return None
        with parser:
            metadata = extractMetadata(parser)
        if metadata and metadata.has("creation_date"):
            return metadata.get("creation_date").value
    except Exception:
        return None

def sort_files_by_date(source_folder, destination_folder, folder_name_format, progress_callback, log_callback, isQuick=False):
    global is_paused, is_cancelled

    log_callback("Counting total number of files...", replace_line=2)
    total_files = 0

    if isQuick:
        try:
            total_files = len(os.listdir(source_folder))
        except Exception as e:
            log_callback(f"Error accessing source folder: {e}")
            return
        log_callback(f"Total number of files: {total_files}", replace_line=2)
    else:
        for filename in os.listdir(source_folder):
            if is_cancelled:
                log_callback("Process cancelled by the user.")
                start_button.config(state=tk.NORMAL)
                return
            file_path = os.path.join(source_folder, filename)
            if os.path.isfile(file_path) and (os.path.splitext(filename)[1].lower() in image_video_extensions):
                total_files += 1
                log_callback(f"Counting files... Total so far: {total_files}", replace_line=2)
        log_callback(f"Total number of files: {total_files}", replace_line=2)

    processed_files = 0

    for filename in os.listdir(source_folder):
        if is_cancelled:
            log_callback("Process cancelled by the user.")
            start_button.config(state=tk.NORMAL)
            return

        file_path = os.path.join(source_folder, filename)
        ext = os.path.splitext(filename)[1].lower()

        if os.path.isdir(file_path) or (ext not in image_video_extensions):
            continue

        try:
            # Try EXIF (for images)
            date_taken = get_exif_date_taken(file_path) if ext in ['.jpg', '.jpeg', '.tiff'] else None

            # Try video metadata if not image
            if not date_taken and ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']:
                date_taken = get_video_creation_date(file_path)

            # Fallback to file modification date
            if not date_taken:
                modification_time = os.path.getmtime(file_path)
                date_taken = datetime.fromtimestamp(modification_time)

            folder_name = date_taken.strftime(folder_name_format)
            target_folder = os.path.join(destination_folder, folder_name)

            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            shutil.move(file_path, os.path.join(target_folder, filename))
            log_callback(f'Moved: {filename} to {target_folder}')

            if is_cancelled:
                log_callback("Cancelling process...")
                log_callback("Process cancelled by the user.")
                start_button.config(state=tk.NORMAL)
                return

        except Exception as e:
            log_callback(f'Error processing {filename}: {e}')

        processed_files += 1
        progress_percentage = (processed_files / total_files) * 100
        progress_callback(progress_percentage)

        while is_paused:
            time.sleep(0.1)

        time.sleep(0.1)

    log_callback("Sorting complete!")
    start_button.config(state=tk.NORMAL)

def update_progress(progress):
    progress_var.set(progress)

def log_message(message, replace_line=None):
    if replace_line is not None:
        log_text.delete(f"{replace_line}.0", f"{replace_line}.end")
        log_text.insert(f"{replace_line}.0", f"{message}\n")
    else:
        log_text.insert(tk.END, f"{message}\n")
        log_text.see(tk.END)

def browse_directory(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_selected)

def update_example_label(*args):
    folder_format = FOLDER_NAME_FORMATS[folder_format_var.get()]
    current_date = datetime.now()
    example_folder_name = current_date.strftime(folder_format)
    example_label.config(text=f"Example: {example_folder_name}")

def start_sorting():
    global is_paused, is_cancelled
    is_paused = False
    is_cancelled = False

    source_folder = source_entry.get()
    destination_folder = destination_entry.get()
    folder_name_format = FOLDER_NAME_FORMATS[folder_format_var.get()]
    is_quick_mode = quick_mode_var.get()

    if not os.path.isdir(source_folder):
        messagebox.showerror("Error", "Invalid source folder.")
        return
    if not os.path.isdir(destination_folder):
        messagebox.showerror("Error", "Invalid destination folder.")
        return

    start_button.config(state=tk.DISABLED)
    progress_var.set(0)
    log_text.delete(1.0, tk.END)

    threading.Thread(target=sort_files_by_date, args=(source_folder, destination_folder, folder_name_format, update_progress, log_message, is_quick_mode), daemon=True).start()

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    pause_button.config(text="Resume" if is_paused else "Pause")
    log_message("Process paused." if is_paused else "Process resumed.")

def cancel_sorting():
    global is_cancelled
    if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the sorting process?"):
        is_cancelled = True
        log_message("Cancelling process...")

def reset_for_new_sort():
    global is_quick_mode
    is_quick_mode = False
    source_entry.delete(0, tk.END)
    destination_entry.delete(0, tk.END)
    folder_format_var.set("YYYY-MM")
    progress_var.set(0)
    log_text.delete(1.0, tk.END)
    start_button.config(state=tk.NORMAL)

app = tk.Tk()
app.title("Photo Sorter v1.3")
app.minsize(600, 400)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, maximum=100, variable=progress_var)
progress_bar.grid(row=5, column=0, columnspan=4, padx=30, pady=10, sticky="ew")

tk.Label(app, text="Source Folder:").grid(row=0, column=0, padx=30, pady=10, sticky="w")
source_entry = tk.Entry(app, width=50)
source_entry.grid(row=0, column=1, padx=10, sticky="ew")
tk.Button(app, text="Browse", command=lambda: browse_directory(source_entry)).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Destination Folder:").grid(row=1, column=0, padx=30, pady=10, sticky="w")
destination_entry = tk.Entry(app, width=50)
destination_entry.grid(row=1, column=1, padx=10, sticky="ew")
tk.Button(app, text="Browse", command=lambda: browse_directory(destination_entry)).grid(row=1, column=2, padx=10, pady=10)

tk.Label(app, text="Folder Name Format:").grid(row=2, column=0, padx=30, pady=10, sticky="w")
folder_format_var = tk.StringVar(value="YYYY-MM")
folder_format_dropdown = ttk.Combobox(app, textvariable=folder_format_var, values=list(FOLDER_NAME_FORMATS.keys()), state="readonly")
folder_format_dropdown.grid(row=2, column=1, padx=10, sticky="ew")
folder_format_dropdown.bind("<<ComboboxSelected>>", update_example_label)

example_label = tk.Label(app, text="Example: YYYY-MM")
example_label.grid(row=2, column=2, padx=10, pady=10, sticky="w")

quick_mode_var = tk.BooleanVar()
quick_mode_checkbox = tk.Checkbutton(app, text="Quick Mode", variable=quick_mode_var)
quick_mode_checkbox.grid(row=4, column=0, columnspan=4, padx=30, pady=10)

start_button = tk.Button(app, text="Start Sorting", command=start_sorting, width=20)
start_button.grid(row=3, column=0, padx=30, pady=10)

new_sort_button = tk.Button(app, text="New Sort", command=reset_for_new_sort, width=20)
new_sort_button.grid(row=3, column=1, padx=10, pady=10)

pause_button = tk.Button(app, text="Pause", command=toggle_pause, width=20)
pause_button.grid(row=3, column=2, padx=10, pady=10)

cancel_button = tk.Button(app, text="Cancel", command=cancel_sorting, width=20)
cancel_button.grid(row=3, column=3, padx=10, pady=10)

log_text = tk.Text(app, width=80, height=10, state=tk.NORMAL)
log_text.grid(row=6, column=0, columnspan=4, padx=30, pady=10, sticky="ew")

app.mainloop()
