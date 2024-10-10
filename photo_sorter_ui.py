# Filename: photo_sorter_ui.py
import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time

# Global control flags
is_paused = False
is_cancelled = False

# Predefined folder name formats for the dropdown
FOLDER_NAME_FORMATS = {
    "YYYY-MM": "%Y-%m",
    "Month-YYYY": "%B-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    # "Day, DD Month YYYY": "%A, %d %B %Y"
}

# Define accepted image and video file extensions
image_video_extensions = {
    # Image Extensions
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.webp', '.heif', '.heic',
    # RAW Image Formats
    '.cr2', '.crw', '.nef', '.nrw', '.orf', '.pef', '.raf', '.rw2', '.dng',
    # Video Extensions
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.webm'
}

# Function to sort and move files based on date modified/taken
def sort_files_by_date(source_folder, destination_folder, folder_name_format, progress_callback, log_callback, isQuick=False):
    global is_paused, is_cancelled
    
    # Log that we are starting the file counting process in a fixed line
    log_callback("Counting total number of files...", replace_line=2)

    total_files = 0

    # Start counting total files based on the isQuick flag
    if isQuick:
        # FAST way: Count all files (including folders) in the source folder
        try:
            total_files = len(os.listdir(source_folder))  # Just a quick count
        except Exception as e:
            log_callback(f"Error accessing source folder: {e}")
            return
        
        # Log the final total file count in place
        log_callback(f"Total number of files: {total_files}", replace_line=2)
        
    else:
        # SLOW way: Count only image and video files
        for filename in os.listdir(source_folder):
            # Check for cancellation after every file check
            if is_cancelled:
                # log_callback("Cancelling process...")
                log_callback("Process cancelled by the user.")
                start_button.config(state=tk.NORMAL)
                return
            
            file_path = os.path.join(source_folder, filename)
            if os.path.isfile(file_path) and (os.path.splitext(filename)[1].lower() in image_video_extensions):
                total_files += 1
                # Update the total files log on line 2
                log_callback(f"Counting files... Total so far: {total_files}", replace_line=2)

        # Log the final total file count in place
        log_callback(f"Total number of files: {total_files}", replace_line=2)

    processed_files = 0

    for filename in os.listdir(source_folder):
        # Check for cancellation at the beginning of each iteration
        if is_cancelled:
            # log_callback("Cancelling process...")
            log_callback("Process cancelled by the user.")
            start_button.config(state=tk.NORMAL)
            return

        file_path = os.path.join(source_folder, filename)

        # Skip directories and non-supported files
        if os.path.isdir(file_path) or (os.path.splitext(filename)[1].lower() not in image_video_extensions):
            continue

        try:
            # Get file's modification date
            modification_time = os.path.getmtime(file_path)
            date_taken = datetime.fromtimestamp(modification_time)

            # Format folder name based on user input
            folder_name = date_taken.strftime(folder_name_format)
            target_folder = os.path.join(destination_folder, folder_name)

            # Create the target folder if it doesn't exist
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # Move the file to the respective folder
            shutil.move(file_path, os.path.join(target_folder, filename))
            log_callback(f'Moved: {filename} to {target_folder}')

            # Check for cancellation immediately after moving the file
            if is_cancelled:
                log_callback("Cancelling process...")
                log_callback("Process cancelled by the user.")
                start_button.config(state=tk.NORMAL)
                return

        except Exception as e:
            log_callback(f'Error processing {filename}: {e}')

        processed_files += 1
        # Update progress
        progress_percentage = (processed_files / total_files) * 100
        progress_callback(progress_percentage)

        # Check if paused
        while is_paused:
            time.sleep(0.1)

        time.sleep(0.1)  # Simulate processing time for demonstration

    log_callback("Sorting complete!")
    start_button.config(state=tk.NORMAL)

# Function to update progress bar
def update_progress(progress):
    progress_var.set(progress)

# Function to log messages
def log_message(message, replace_line=None):
    if replace_line is not None:
        # Replace the content of a specific line (1-based index)
        log_text.delete(f"{replace_line}.0", f"{replace_line}.end")
        log_text.insert(f"{replace_line}.0", f"{message}\n")
    else:
        # Default behavior: Append the message to the log
        log_text.insert(tk.END, f"{message}\n")
        log_text.see(tk.END)  # Scroll to the end

# Helper function to browse and set folder path
def browse_directory(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:  # Check if a valid folder was selected
        entry_widget.delete(0, tk.END)  # Clear the current text in the Entry widget
        entry_widget.insert(0, folder_selected)  # Insert the new folder path

# Function to update example label when folder format is changed
def update_example_label(*args):
    folder_format = FOLDER_NAME_FORMATS[folder_format_var.get()]
    current_date = datetime.now()
    example_folder_name = current_date.strftime(folder_format)
    example_label.config(text=f"Example: {example_folder_name}")

# Function to start sorting when user clicks the button
def start_sorting():
    global is_paused, is_cancelled
    is_paused = False
    is_cancelled = False

    source_folder = source_entry.get()
    destination_folder = destination_entry.get()
    folder_name_format = FOLDER_NAME_FORMATS[folder_format_var.get()]

    # Validate input
    if not os.path.isdir(source_folder):
        messagebox.showerror("Error", "Invalid source folder.")
        return

    if not os.path.isdir(destination_folder):
        messagebox.showerror("Error", "Invalid destination folder.")
        return

    # Disable start button and reset progress
    start_button.config(state=tk.DISABLED)
    progress_var.set(0)
    log_text.delete(1.0, tk.END)  # Clear previous logs

    # Start sorting in a new thread
    threading.Thread(target=sort_files_by_date, args=(source_folder, destination_folder, folder_name_format, update_progress, log_message), daemon=True).start()

# Function to pause/resume sorting
def toggle_pause():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        pause_button.config(text="Resume")
        log_message("Process paused.")
    else:
        pause_button.config(text="Pause")
        log_message("Process resumed.")

# Function to cancel sorting
def cancel_sorting():
    global is_cancelled
    if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the sorting process?"):
        is_cancelled = True
        log_message("Cancelling process...")

# Function to reset the UI for a new sort
def reset_for_new_sort():
    # Clear all input fields
    source_entry.delete(0, tk.END)
    destination_entry.delete(0, tk.END)

    # Reset the dropdown to the default value
    folder_format_var.set("YYYY-MM")

    # Clear progress bar and logs
    progress_var.set(0)
    log_text.delete(1.0, tk.END)

    # Re-enable the "Start Sorting" button
    start_button.config(state=tk.NORMAL)

# Create the UI window
app = tk.Tk()
app.title("Photo Sorter")
# app.iconphoto(False, tk.PhotoImage(file="appicon.png"))  # Set custom icon for the window

# Set minimum window size to 600px wide and 400px tall
app.minsize(600, 400)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, maximum=100, variable=progress_var)
progress_bar.grid(row=5, column=0, columnspan=4, padx=30, pady=10, sticky="ew")  # Full-width with padding

# Source Folder Input
tk.Label(app, text="Source Folder:").grid(row=0, column=0, padx=30, pady=10, sticky="w")
source_entry = tk.Entry(app, width=50)
source_entry.grid(row=0, column=1, padx=10, sticky="ew")
tk.Button(app, text="Browse", command=lambda: browse_directory(source_entry)).grid(row=0, column=2, padx=10, pady=10)

# Destination Folder Input
tk.Label(app, text="Destination Folder:").grid(row=1, column=0, padx=30, pady=10, sticky="w")
destination_entry = tk.Entry(app, width=50)
destination_entry.grid(row=1, column=1, padx=10, sticky="ew")
tk.Button(app, text="Browse", command=lambda: browse_directory(destination_entry)).grid(row=1, column=2, padx=10, pady=10)

# Folder Name Format Dropdown
tk.Label(app, text="Folder Name Format:").grid(row=2, column=0, padx=30, pady=10, sticky="w")
folder_format_var = tk.StringVar(value="YYYY-MM")
folder_format_dropdown = ttk.Combobox(app, textvariable=folder_format_var, values=list(FOLDER_NAME_FORMATS.keys()), state="readonly")
folder_format_dropdown.grid(row=2, column=1, padx=10, sticky="ew")
folder_format_dropdown.bind("<<ComboboxSelected>>", update_example_label)  # Update example on selection change

# Example Folder Name Label
example_label = tk.Label(app, text="Example: YYYY-MM")
example_label.grid(row=2, column=2, padx=10, pady=10, sticky="w")

# Start Sorting Button
start_button = tk.Button(app, text="Start Sorting", command=start_sorting, width=20)
start_button.grid(row=3, column=0, padx=30, pady=10)

# New Sort Button
new_sort_button = tk.Button(app, text="New Sort", command=reset_for_new_sort, width=20)
new_sort_button.grid(row=3, column=1, padx=10, pady=10)

# Pause/Resume Button
pause_button = tk.Button(app, text="Pause", command=toggle_pause, width=20)
pause_button.grid(row=3, column=2, padx=10, pady=10)

# Cancel Button
cancel_button = tk.Button(app, text="Cancel", command=cancel_sorting, width=20)
cancel_button.grid(row=3, column=3, padx=10, pady=10)

# Log Messages Text Box
log_text = tk.Text(app, width=80, height=10, state=tk.NORMAL)
log_text.grid(row=6, column=0, columnspan=4, padx=30, pady=10, sticky="ew")

# Run the application
app.mainloop()
