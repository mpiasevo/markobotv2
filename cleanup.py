import os
import time

def clean():
    print("File Cleanup Initiated")
    directory = os.getcwd()

    files_in_directory = os.listdir(directory)
    files = 0
    filtered_files = [file for file in files_in_directory if file.endswith(".webm")]
    for file in filtered_files:
        files = files + 1
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)
        print(files, 'Files Deleted')
    if files == 0:
        print("No Cleanup Needed")

