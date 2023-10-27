#!/usr/bin/env python3
import os
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import shutil

# Define the directory paths
import sys

if len(sys.argv) != 3:
    print("Usage: python program.py <input_directory> <output_directory>")
    sys.exit(1)

input_directory = sys.argv[1]
output_directory = sys.argv[2]

# Create subdirectories if they don't exist
os.makedirs(output_directory, exist_ok=True)

sys.abort()

# Load the MobileNetV2 model from TensorFlow Hub
model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
model = tf.keras.Sequential([hub.KerasLayer(model_url)])

# Initialize a dictionary to store user-modified paths
user_modified_paths = {}

def classify_and_sort_image(image_path):
    # Load and preprocess the image
    img = tf.keras.utils.get_file('image.jpg', image_path)
    img = tf.io.read_file(img)
    img = tf.image.decode_image(img)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, (224, 224))
    img = img[tf.newaxis, ...]

    # Classify the image
    predictions = model.predict(img)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions.numpy())

    if decoded_predictions:
        top_prediction = decoded_predictions[0][0][1]
        sorted_path = os.path.join(output_directory, top_prediction)

        # Check if the path exists and ask the user for feedback
        if os.path.exists(sorted_path):
            while True:
                print(f"Image: {filename} sorted into: {sorted_path}")
                user_input = input("Enter new path or 'q' to stop: ")
                if user_input == 'q':
                    return sorted_path
                else:
                    user_modified_paths[filename] = user_input
                    sorted_path = user_input
        return sorted_path

    return os.path.join(output_directory, "unsorted")

# Loop through images in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        image_path = os.path.join(input_directory, filename)
        sorted_path = classify_and_sort_image(image_path)

        # Move the image to the sorted path
        shutil.move(image_path, os.path.join(sorted_path, filename))

# Update user-modified paths
with open('user_modified_paths.txt', 'w') as file:
    for filename, path in user_modified_paths.items():
        file.write(f"{filename}:{path}\n")
