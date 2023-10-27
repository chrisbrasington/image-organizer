#!/usr/bin/env python3
import os
import shutil
import sys
# import PIL.Image
import subprocess
import time

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
file_path = 'user_modified_paths.txt'
if not os.path.exists(file_path):
    open(file_path, 'w').close()
with open(file_path, 'r') as file:
    unique_paths = [line.strip() for line in file.readlines()]

ASCII_CHARS = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]

import math

def resize(image, new_width=100):
    old_width, old_height = image.size
    
    new_height = math.floor(new_width * old_height / old_width)
    new_width = math.floor(new_width)

    print(new_width, new_height)

    return image.resize((new_width, new_height))

def to_greyscale(image):
    return image.convert("L")

def pixel_to_ascii(image):
    pixels = image.getdata()
    ascii_str = "";
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel//25];
    return ascii_str

# Loop through images in the input directory
for filename in os.listdir(input_directory):
    if filename.startswith('.trashed'):
        continue

    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        # open and resize the image
        image_path = os.path.join(input_directory, filename)   
        
        print(image_path)
        subprocess_viewer = subprocess.Popen(f'xdg-open "{image_path}"', shell=True)

        time.sleep(0.8)
        subprocess.call(["wmctrl", "-a", "code"])

        # #resize image
        # image = PIL.Image.open(image_path)
        # image = resize(image);
        # #convert image to greyscale image
        # greyscale_image = to_greyscale(image)
        # # convert greyscale image to ascii characters
        # ascii_str = pixel_to_ascii(greyscale_image)
        # img_width = greyscale_image.width
        # ascii_str_len = len(ascii_str)
        # ascii_img=""
        # #Split the string based on width  of the image
        # for i in range(0, ascii_str_len, img_width):
        #     ascii_img += ascii_str[i:i+img_width] + "\n"

        # print(ascii_img)

        skip = False

        # Ask the user for a file path to move the image to
        while True:
            selected_path = None

            print(f"Image: {filename}")
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
                print(selected_path)
            else:
                # selected_path = os.path.join(output_directory, user_input)
                # unique_paths.append(selected_path)

                potentially_new_path = os.path.join(output_directory, user_input)

                selected_path = None
                match = 0
                for path in unique_paths:
                    if user_input in path:
                        selected_path = path
                        print(selected_path)
                        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        match += 1
                if match > 1:
                    print('Multiple matches found. Please try again.')
                    continue
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
        subprocess.call(["killall", 'eog'])

        # Move the image to the selected path
        if not skip:
            shutil.move(image_path, os.path.join(selected_path, filename))

    # Display all the prior paths
    # print("Prior paths:")
    # for i, path in enumerate(unique_paths):
    #     print(f"{i+1} - {path}")

    # Update user-modified paths
    with open('user_modified_paths.txt', 'w') as file:
        for i, path in enumerate(unique_paths):
            file.write(f"{path}\n")
