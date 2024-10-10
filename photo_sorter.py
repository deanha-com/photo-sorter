# Filename: photo_sorter.py
import os
import shutil
from datetime import datetime

# Set the path to your ImportedPhotos folder
source_folder = r'C:\Users\Dean Ha\Pictures\ImportedPhotos'

# Destination folder where files will be sorted into (optional)
# Set as the same path as source_folder to organize in-place
destination_folder = source_folder  

# Create subfolders based on the year and month of file modification/taken date
def sort_files_by_date(folder_path, destination_path):
    # Get all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip if it's a directory
        if os.path.isdir(file_path):
            continue

        try:
            # Get the file's modification time
            modification_time = os.path.getmtime(file_path)
            date_taken = datetime.fromtimestamp(modification_time)

            # Create folder name based on year and month (e.g., '2024-08')
            folder_name = date_taken.strftime('%Y-%m')
            target_folder = os.path.join(destination_path, folder_name)

            # Create the target folder if it doesn't exist
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # Move the file to the respective folder
            shutil.move(file_path, os.path.join(target_folder, filename))
            print(f'Moved: {filename} to {target_folder}')
        
        except Exception as e:
            print(f'Error processing {filename}: {e}')

# Run the script
if __name__ == "__main__":
    sort_files_by_date(source_folder, destination_folder)
