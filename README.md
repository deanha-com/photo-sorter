# Photo Sorter Application

This application sorts image and video files into folders based on their date modified/taken. It is built using Python and Tkinter for the user interface.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Script](#running-the-script)
- [Packaging with PyInstaller](#packaging-with-pyinstaller)
- [Adding PyInstaller to PATH](#adding-pyinstaller-to-path)
- [Finding the Packaged .exe File](#finding-the-packaged-exe-file)

## Requirements

- Python 3.6 or higher
- Tkinter (comes pre-installed with Python)
- Additional packages:
  - `shutil`
  - `os`
  - `datetime`

These libraries are part of the Python standard library, so you typically won't need to install them separately.

## Installation

1. **Download Python**: If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and follow the installation instructions.

2. **Install Required Packages**: Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux) and run the following command to ensure that you have all required packages:

   ```bash
   pip install --upgrade pip
   ```

## Running the Script {#running-the-script}

---

1.  **Clone the Repository or Download the Script**: Make sure you have the script file (e.g., `photo_sorter_ui.py`) saved locally.
2.  **Open a Terminal or Command Prompt**: Navigate to the directory where your script is located.
3.  **Run the Script**: Execute the script using Python:

    ```bash
    `python photo_sorter_ui.py`
    ```

4.  **Follow the On-Screen Instructions**: The application will guide you through the process of selecting the source and destination folders and configuring the sorting options.

## Packaging with PyInstaller

---

To create a standalone executable of the application, you can use PyInstaller.

1.  **Install PyInstaller**: Run the following command in your terminal:

    ```bash
    `pip install pyinstaller`
    ```

2.  **Navigate to Your Script's Directory**: Use the terminal to go to the directory containing your script:

    ```bash
    `cd path\to\your\script`
    ```

3.  **Package the Script**: Run the following command to create an executable:

    ```bash
    `pyinstaller --onefile --windowed photo_sorter_ui.py`
    ```

- `--onefile` creates a single executable file.
- `--windowed` prevents a console window from appearing when the application is run.

## Adding PyInstaller to PATH {#adding-pyinstaller-to-path}

---

If you want to run `pyinstaller` from any directory, make sure the Scripts directory of your Python installation is added to your PATH.

1.  **Find the Scripts Directory**: This is typically located at `C:\PythonXX\Scripts` on Windows, where `XX` is your Python version (e.g., `C:\Python39\Scripts`).
2.  **Add to PATH**:

    - **Windows**:
      1.  Search for "Environment Variables" in the Start menu.
      2.  Click on "Edit the system environment variables."
      3.  In the System Properties window, click on "Environment Variables."
      4.  Under "System variables," find and select the "Path" variable, then click "Edit."
      5.  Click "New" and add the path to the Scripts directory.
      6.  Click "OK" to close all dialogs.
    - **macOS/Linux**: Add the following line to your `.bashrc`, `.bash_profile`, or `.zshrc` file:

      ```bash
      `export PATH="$PATH:/path/to/python/Scripts"`
      ```

## Finding the Packaged .exe File

---

After packaging the script with PyInstaller, you can find the `.exe` file in the `dist` directory within your script's folder.

1.  **Locate the `dist` Directory**: In the same directory as your script, you should see a folder named `dist`.
2.  **Find the Executable**: Inside the `dist` folder, you will find the executable file named `photo_sorter_ui.exe`.
3.  **Run the Executable**: You can double-click the `.exe` file to run the application directly.

## License

---

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
