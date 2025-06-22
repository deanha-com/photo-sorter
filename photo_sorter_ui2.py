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
is_quick_mode = False  # New variable to track quick mode

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
    '.raf', '.cr2', '.rw2', '.erf', '.nrw', '.nef', '.rwz', '.dng', '.arw', '.eip', '.bay', '.dcr', '.gpr', '.raw', '.crw', '.3fr', '.sr2', '.k25', '.dng', '.mef', '.kc2', '.cs1', '.mos', '.orf', '.kdc', '.cr3', '.srf', '.srw', '.j6i', '.ari', '.fff', '.mrw', '.mfw', '.rwl', '.x3f', '.pef', '.iiq', '.cxi', '.nksc',
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
                log_callback("Process cancelled by the user.")
                reset_ui_for_new_sort()
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
            log_callback("Process cancelled by the user.")
            reset_ui_for_new_sort()
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
                log_callback("Process cancelled by the user.")
                reset_ui_for_new_sort()
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
    reset_ui_for_new_sort()

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

# Function to reset UI for new sort
def reset_ui_for_new_sort():
    global is_paused, is_cancelled, is_quick_mode
    is_paused = False
    is_cancelled = False
    is_quick_mode = False

    # Reset buttons
    start_button.grid()  # Show start button
    cancel_button.grid_remove()  # Hide cancel button
    pause_button.grid_remove()  # Hide pause button
    pause_button.config(text="Pause")  # Reset pause button text to "Pause"

    # Re-enable Start button
    start_button.config(state=tk.NORMAL)

    # Reset log, progress, and inputs
    progress_var.set(0)
    log_text.delete(1.0, tk.END)  # Clear log
    source_entry.delete(0, tk.END)
    destination_entry.delete(0, tk.END)

# Function to start sorting when user clicks the button
def start_sorting():
    global is_paused, is_cancelled  # Removed is_quick_mode from here
    is_paused = False
    is_cancelled = False

    source_folder = source_entry.get()
    destination_folder = destination_entry.get()
    folder_name_format = FOLDER_NAME_FORMATS[folder_format_var.get()]

    # Get quick mode state directly from the checkbox
    is_quick_mode = quick_mode_var.get()  # Read the current value of the checkbox

    # Validate input
    if not os.path.isdir(source_folder):
        messagebox.showerror("Error", "Invalid source folder.")
        return

    if not os.path.isdir(destination_folder):
        messagebox.showerror("Error", "Invalid destination folder.")
        return

    # Hide start button, show cancel and pause buttons
    start_button.grid_remove()  # Hide start button
    cancel_button.grid()  # Show cancel button
    pause_button.grid()  # Show pause button

    # Disable start button and reset progress
    progress_var.set(0)
    log_text.delete(1.0, tk.END)  # Clear previous logs

    # Start sorting in a new thread, passing the quick mode option
    threading.Thread(target=sort_files_by_date, args=(source_folder, destination_folder, folder_name_format, update_progress, log_message, is_quick_mode), daemon=True).start()

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

# Create the UI window
app = tk.Tk()
app.title("Photo Sorter")

# Set minimum window size to 600px wide and 400px tall
app.minsize(600, 400)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, maximum=100, variable=progress_var)
progress_bar.grid(row=5, column=0, columnspan=4, padx=30, pady=10, sticky="ew")  # Full-width with padding

# Folder Input: Source
tk.Label(app, text="Source Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
source_entry = tk.Entry(app, width=50)
source_entry.grid(row=0, column=1, padx=10, pady=10)
source_browse_button = tk.Button(app, text="Browse", command=lambda: browse_directory(source_entry))
source_browse_button.grid(row=0, column=2, padx=10, pady=10)

# Folder Input: Destination
tk.Label(app, text="Destination Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
destination_entry = tk.Entry(app, width=50)
destination_entry.grid(row=1, column=1, padx=10, pady=10)
destination_browse_button = tk.Button(app, text="Browse", command=lambda: browse_directory(destination_entry))
destination_browse_button.grid(row=1, column=2, padx=10, pady=10)

# Dropdown for Folder Format
tk.Label(app, text="Folder Name Format:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
folder_format_var = tk.StringVar(value="YYYY-MM")
folder_format_menu = tk.OptionMenu(app, folder_format_var, *FOLDER_NAME_FORMATS.keys())
folder_format_menu.grid(row=2, column=1, padx=10, pady=10)

# Bind update_example_label to the folder format dropdown
folder_format_var.trace_add('write', update_example_label)

# Example folder name label
example_label = tk.Label(app, text="Example: ")
example_label.grid(row=2, column=2, padx=10, pady=10)

# Quick Mode Checkbox
quick_mode_var = tk.BooleanVar()
quick_mode_checkbox = tk.Checkbutton(app, text="Enable Quick Mode", variable=quick_mode_var)
quick_mode_checkbox.grid(row=3, column=0, padx=10, pady=10, sticky="w")

# Log Output (Text Widget)
log_text = tk.Text(app, height=10, width=80)
log_text.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

# Buttons (Start, Pause, Cancel)
start_button = tk.Button(app, text="Start Sorting", command=start_sorting)
start_button.grid(row=7, column=1, padx=10, pady=10)

pause_button = tk.Button(app, text="Pause", command=toggle_pause)
pause_button.grid(row=7, column=2, padx=10, pady=10)
pause_button.grid_remove()  # Hide initially

cancel_button = tk.Button(app, text="Cancel", command=cancel_sorting)
cancel_button.grid(row=7, column=3, padx=10, pady=10)
cancel_button.grid_remove()  # Hide initially

# Start the UI loop
app.mainloop()
