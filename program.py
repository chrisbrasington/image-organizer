#!/usr/bin/env python3
import os
import shutil
import sys
import subprocess
import threading

def run_feh(image_path):
    subprocess.run(["feh", image_path])

if len(sys.argv) != 3:
    print("Usage: python program.py <input_directory> <output_directory>")
    sys.exit(1)

input_directory = sys.argv[1]
output_directory = sys.argv[2]

print('Starting...')
print(input_directory)
print(output_directory)
print()

# Create subdirectories if they don't exist
os.makedirs(output_directory, exist_ok=True)

# Initialize an array to store unique paths
unique_paths = []

# Loop through images in the input directory
for filename in os.listdir(input_directory):
    import time

    # Initialize a global variable to keep track of the feh thread
    feh_thread = None

    # Initialize a threading event to signal the feh thread to stop
    stop_event = threading.Event()

    def run_feh(image_path):
        global stop_event
        while not stop_event.is_set():
            subprocess.run(["feh", image_path])
            time.sleep(1)

    if len(sys.argv) != 3:
        print("Usage: python program.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    print(input_directory)
    print(output_directory)

    # Create subdirectories if they don't exist
    os.makedirs(output_directory, exist_ok=True)

    # Initialize an array to store unique paths
    unique_paths = []

    # Loop through images in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # open with feh on a separate thread
            image_path = os.path.join(input_directory, filename)
            feh_thread = threading.Thread(target=run_feh, args=(image_path,))
            feh_thread.start()

        image_path = os.path.join(input_directory, filename)

        # Ask the user for a file path to move the image to
        while True:
            print(f"Image: {filename}")
            print("Select a path or enter a new path:")
            for i, path in enumerate(unique_paths):
                print(f"{i+1} - {path}")
            user_input = input("Enter path: ")
            if user_input.isdigit() and int(user_input) <= len(unique_paths):
                selected_path = unique_paths[int(user_input)-1]
            else:
                selected_path = os.path.join(output_directory, user_input)
                unique_paths.append(selected_path)
            if os.path.exists(selected_path):
                break
            else:
                print("Invalid path. Please try again.")

        # Kill the feh thread
        stop_event.set()
        if feh_thread is not None:
            feh_thread.join()
        
        # Move the image to the selected path
        shutil.move(image_path, os.path.join(selected_path, filename))

    # Display all the prior paths
    print("Prior paths:")
    for i, path in enumerate(unique_paths):
        print(f"{i+1} - {path}")

    # Update user-modified paths
    with open('user_modified_paths.txt', 'w') as file:
        for i, path in enumerate(unique_paths):
            file.write(f"{i+1}:{path}\n")
