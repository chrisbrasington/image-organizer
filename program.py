#!/usr/bin/env python3
import os
import shutil
import sys
# import PIL.Image
import subprocess
import time
import math

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
user_modified_paths_file = 'user_modified_paths.txt'
script_dir = os.path.dirname(os.path.abspath(__file__))
user_modified_paths_file = os.path.join(script_dir, user_modified_paths_file)
if not os.path.exists(user_modified_paths_file):
    open(user_modified_paths_file, 'w').close()
with open(user_modified_paths_file, 'r') as file:
    unique_paths = [line.strip() for line in file.readlines()]

number_of_files = len(os.listdir(input_directory))
count = 0

# Loop through images in the input directory
for filename in os.listdir(input_directory):
    if filename.startswith('.trashed'):
        continue

    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', 'webp', 'jfif')):
        # open and resize the image
        image_path = os.path.join(input_directory, filename)   
        
        subprocess_viewer = subprocess.Popen(f'xdg-open "{image_path}"', shell=True)

        time.sleep(0.8)
        subprocess.call(["wmctrl", "-a", "code"])

        count += 1

        skip = False

        # Ask the user for a file path to move the image to
        while True:
            selected_path = None

            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(f"{count}/{number_of_files} - {image_path}")
            # for i, path in enumerate(unique_paths):
            #     print(f"{i+1} - {path}")

            user_input = input("Select (or type new): ")

            if user_input == 'new':
                user_input = input("Enter new path: ")
                user_input = os.path.join(output_directory, user_input)
                unique_paths.append(user_input)
                selected_path = user_input
                unique_paths = sorted(unique_paths)
                continue

            if user_input == 'd':
                print('deleting')
                
                selected_path = os.path.join(output_directory, 'trash')
                if not os.path.exists(selected_path):
                    os.makedirs(selected_path)
                shutil.move(image_path, os.path.join(selected_path, filename))
                skip = True
                
                break

            if user_input == 'q' or user_input == 'exit':
                if subprocess_viewer is not None:
                    subprocess_viewer.terminate()

                subprocess.call(["killall", 'eog'])
                sys.exit(0)

            if user_input.isdigit() and int(user_input) <= len(unique_paths):
                selected_path = unique_paths[int(user_input)-1]
                
            else:
                # selected_path = os.path.join(output_directory, user_input)
                # unique_paths.append(selected_path)

                potentially_new_path = os.path.join(output_directory, user_input)

                selected_path = None
                match = 0

                if(user_input.startswith('/')):
                    paths = [path for path in unique_paths if path.endswith(user_input)]

                    if len(paths) >1:
                        for path in paths:
                            print(path)

                    if len(paths) == 1:
                        match = 1
                        selected_path = paths[0]
                else:
                    for path in unique_paths:
                        if user_input in path:
                            selected_path = path
                            print(path)
                            match += 1

                if match > 1:

                    if not user_input.startswith('/'):
                        user_input = '/' + user_input

                    ends_with_path = [path for path in unique_paths if path.endswith(user_input)]

                    if len(ends_with_path) == 1:
                        ends_with_path = ends_with_path[0]
                        print(f'Multiple paths exists, but using endswith: {ends_with_path}')
                        selected_path = ends_with_path
                    else:
                        print('Multiple matches found. Please try again.')
                        continue
                # elif match == 1:
                    
                if selected_path is None:
                    print("Path is new")
                    yesno = input(f'Use {potentially_new_path} (y/n)?')
                    if yesno == 'y':
                        selected_path = potentially_new_path
                        unique_paths.append(selected_path)
                    else:
                        continue

            unique_paths = sorted(unique_paths)

            if not os.path.exists(selected_path):
                os.makedirs(selected_path)

            if os.path.exists(selected_path):
                break
            else:
                print("Invalid path. Please try again.")

        if subprocess_viewer is not None:
            subprocess_viewer.terminate()
        subprocess.call(["killall", 'eog'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.call(["killall", 'feh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Move the image to the selected path
        if not skip:
            shutil.move(image_path, os.path.join(selected_path, filename))

    # Display all the prior paths
    # print("Prior paths:")
    # for i, path in enumerate(unique_paths):
    #     print(f"{i+1} - {path}")

    # Update user-modified paths
    with open(user_modified_paths_file, 'w') as file:
        for i, path in enumerate(unique_paths):
            file.write(f"{path}\n")
