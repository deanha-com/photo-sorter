# Filename: photo_sorter_v2.py

import flet as ft
import os
import shutil
import threading
import time
from datetime import datetime
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# Supported file extensions
image_video_extensions = {
    # Image Extensions
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.webp', '.heif', '.heic',
    # RAW Image Formats
    '.raf', '.cr2', '.rw2', '.erf', '.nrw', '.nef', '.rwz', '.dng', '.arw', '.eip', '.bay', '.dcr', '.gpr', '.raw', '.crw', '.3fr', '.sr2', '.k25', '.dng', '.mef', '.kc2', '.cs1', '.mos', '.orf', '.kdc', '.cr3', '.srf', '.srw', '.j6i', '.ari', '.fff', '.mrw', '.mfw', '.rwl', '.x3f', '.pef', '.iiq', '.cxi', '.nksc',
    # Video Extensions
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.webm'
}

# Folder name formats
FOLDER_NAME_FORMATS = {
    "YYYY-MM": "%Y-%m",
    "Month-YYYY": "%B-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
}

# State variables
is_paused = False
is_cancelled = False

def get_date_taken(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in {".jpg", ".jpeg", ".tiff"}:
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                date_taken = exif_data.get(36867) or exif_data.get(306)
                if date_taken:
                    return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

    try:
        parser = createParser(file_path)
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata and metadata.has("creation_date"):
                    return metadata.get("creation_date").value
    except Exception:
        pass

    return datetime.fromtimestamp(os.path.getmtime(file_path))

def sort_files(source, destination, folder_format, log, progress):
    global is_paused, is_cancelled

    all_files = [f for f in os.listdir(source) if os.path.splitext(f)[1].lower() in image_video_extensions]
    total = len(all_files)
    count = 0

    if total == 0:
        log("⚠️ No supported files found in source folder.")
        return

    for filename in all_files:
        if is_cancelled:
            log("⛔ Cancelled.")
            return

        while is_paused:
            time.sleep(0.2)

        src_path = os.path.join(source, filename)
        try:
            date_taken = get_date_taken(src_path)
            folder_name = date_taken.strftime(folder_format)
            target_folder = os.path.join(destination, folder_name)
            os.makedirs(target_folder, exist_ok=True)

            shutil.move(src_path, os.path.join(target_folder, filename))
            log(f"✅ Moved: {filename} → {folder_name}")

        except Exception as e:
            log(f"❌ Error: {filename} - {e}")

        count += 1
        progress.value = (count / total)
        progress.update()

    progress.value = 1.0
    progress.update()
    log("🎉 Sorting Complete!")

def main(page: ft.Page):
    page.title = "Photo Sorter v2.0"
    page.window_min_width = 600
    page.window_min_height = 500
    page.theme_mode = ft.ThemeMode.LIGHT

    source = ft.TextField(label="Source Folder", expand=True)
    destination = ft.TextField(label="Destination Folder", expand=True)
    folder_format = ft.Dropdown(
        label="Folder Format",
        options=[ft.dropdown.Option(k) for k in FOLDER_NAME_FORMATS.keys()],
        value="YYYY-MM"
    )

    format_preview = ft.Text(value=f"Preview: {datetime.now().strftime(FOLDER_NAME_FORMATS[folder_format.value])}")

    def update_format_preview(e):
        fmt = FOLDER_NAME_FORMATS.get(folder_format.value, "%Y-%m")
        format_preview.value = f"Preview: {datetime.now().strftime(fmt)}"
        format_preview.update()

    folder_format.on_change = update_format_preview

    log_output = ft.TextField(multiline=True, read_only=True, expand=True, min_lines=10, max_lines=20)
    progress = ft.ProgressBar(width=400, value=0)

    def log(msg):
        log_output.value += msg + "\n"
        log_output.update()

    def browse_folder(ctrl: ft.TextField):
        def result(e: ft.FilePickerResultEvent):
            if e.path:
                ctrl.value = e.path
                ctrl.update()

        picker = ft.FilePicker(on_result=result)
        page.overlay.append(picker)
        page.update()
        picker.get_directory_path()

    def start_sorting(e):
        global is_paused, is_cancelled
        is_paused = False
        is_cancelled = False
        log_output.value = ""
        progress.value = 0
        page.update()

        if not os.path.isdir(source.value) or not os.path.isdir(destination.value):
            log("⚠️ Invalid folder(s). Please check paths.")
            return

        fmt = FOLDER_NAME_FORMATS[folder_format.value]
        threading.Thread(
            target=sort_files,
            args=(source.value, destination.value, fmt, log, progress),
            daemon=True
        ).start()

    def pause_resume(e):
        global is_paused
        is_paused = not is_paused
        pause_btn.text = "▶ Resume" if is_paused else "⏸ Pause"
        pause_btn.update()

    def cancel(e):
        global is_cancelled
        is_cancelled = True

    pause_btn = ft.ElevatedButton("⏸ Pause", on_click=pause_resume)

    page.add(
        ft.Row([source, ft.IconButton(icon="folder_open", on_click=lambda _: browse_folder(source))]),
        ft.Row([destination, ft.IconButton(icon="folder_open", on_click=lambda _: browse_folder(destination))]),
        folder_format,
        format_preview,
        ft.Row([
            ft.ElevatedButton("🚀 Start Sorting", on_click=start_sorting),
            pause_btn,
            ft.ElevatedButton("🛑 Cancel", on_click=cancel)
        ]),
        ft.Container(progress, padding=10),
        log_output
    )

ft.app(target=main)
