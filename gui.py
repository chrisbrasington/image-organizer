#!/usr/bin/env python3
import os
import sys
import shutil
from tkinter import Tk, Label, Entry, Button, PhotoImage, messagebox, StringVar
from PIL import Image, ImageTk

if len(sys.argv) != 3:
    print("Usage: python program.py <input_directory> <output_directory>")
    sys.exit(1)

input_directory = sys.argv[1]
output_directory = sys.argv[2]
os.makedirs(output_directory, exist_ok=True)

unique_paths = []
history_stack = []  # store (src, dest) for undo

user_modified_paths_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_modified_paths.txt')

if not os.path.exists(user_modified_paths_file):
    open(user_modified_paths_file, 'w').close()

with open(user_modified_paths_file, 'r') as file:
    unique_paths = [line.strip() for line in file.readlines()]

image_files = [f for f in os.listdir(input_directory)
               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', 'webp', 'jfif')) and not f.startswith('.trashed')]
total_files = len(image_files)
index = 0


class ImageSorterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Sorter")

        self.image_label = Label(master)
        self.image_label.pack()

        self.info_label = Label(master, text="")
        self.info_label.pack()

        self.entry = Entry(master, width=80)
        self.entry.pack()
        self.entry.bind('<Return>', lambda event: self.submit())

        self.submit_button = Button(master, text="Submit", command=self.submit)
        self.submit_button.pack()

        self.undo_button = Button(master, text="Undo", command=self.undo_last, state="disabled")
        self.undo_button.pack()

        self.delete_button = Button(master, text="Delete", command=self.delete_image)
        self.delete_button.pack()

        self.status_text = StringVar()
        self.status_label = Label(master, textvariable=self.status_text)
        self.status_label.pack()

        self.current_image = None
        self.current_filename = None
        self.skip = False

        self.load_next_image()

    def load_next_image(self):
        global index
        if index >= total_files:
            self.status_text.set("✅ All images processed.")
            self.image_label.config(image='')
            self.info_label.config(text='')
            self.entry.config(state="disabled")
            self.submit_button.config(state="disabled")
            self.delete_button.config(state="disabled")

            # ✅ Show dialog and exit on OK
            messagebox.showinfo("Done", "✅ All images have been processed.")
            self.master.destroy()
            return

        self.skip = False
        self.current_filename = image_files[index]
        image_path = os.path.join(input_directory, self.current_filename)

        # ✅ Print to console
        print(f"Loading image: {image_path}")

        # ✅ Show full path in GUI
        self.info_label.config(text=f"{index+1}/{total_files} - {self.current_filename}\n{image_path}")

        try:
            pil_image = Image.open(image_path)
            pil_image.thumbnail((800, 800))
            self.current_image = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=self.current_image)
        except Exception as e:
            print(f"Failed to load image: {e}")
            self.skip = True
            index += 1
            self.load_next_image()

    def submit(self):
        global index
        user_input = self.entry.get().strip()
        self.entry.delete(0, 'end')

        image_path = os.path.join(input_directory, self.current_filename)

        if user_input in ['q', 'exit']:
            self.master.quit()
            return

        selected_path = None

        if user_input == 'new':
            new_path = os.path.join(output_directory, input("Enter new path in terminal: "))
            unique_paths.append(new_path)
            selected_path = new_path

        elif user_input == 'd':
            # Same as delete button, but through typing 'd'
            self.delete_image()
            return

        elif user_input.isdigit() and int(user_input) <= len(unique_paths):
            selected_path = unique_paths[int(user_input) - 1]

        else:
            potentially_new_path = os.path.join(output_directory, user_input)
            selected_path = None
            match_count = 0

            for path in unique_paths:
                if user_input in path:
                    selected_path = path
                    match_count += 1

            if match_count > 1:
                matches = [p for p in unique_paths if user_input in p]
                msg = "Multiple matching paths found:\n\n" + "\n".join(f"{i+1}. {m}" for i, m in enumerate(matches))
                msg += "\n\nPlease enter a more specific name (or full path segment)."
                messagebox.showwarning("Ambiguous", msg)
                return

            if selected_path is None:
                use_path = messagebox.askyesno("New Path", f"Use new path {potentially_new_path}?")
                if use_path:
                    selected_path = potentially_new_path
                    unique_paths.append(selected_path)
                else:
                    return

        unique_paths.sort()
        os.makedirs(selected_path, exist_ok=True)

        if not self.skip:
            dest_path = os.path.join(selected_path, self.current_filename)
            shutil.move(image_path, dest_path)
            history_stack.append((dest_path, input_directory))
            self.undo_button.config(state="normal")
            self.status_text.set(f"✅ Moved to: {dest_path}")

        with open(user_modified_paths_file, 'w') as file:
            for path in unique_paths:
                file.write(path + '\n')

        index += 1
        self.load_next_image()

    def delete_image(self):
        global index
        if not self.current_filename:
            return

        image_path = os.path.join(input_directory, self.current_filename)
        selected_path = os.path.join(output_directory, 'trash')
        os.makedirs(selected_path, exist_ok=True)

        dest_path = os.path.join(selected_path, self.current_filename)
        try:
            shutil.move(image_path, dest_path)
            history_stack.append((dest_path, input_directory))
            self.undo_button.config(state="normal")
            self.status_text.set(f"🗑️ Deleted to: {dest_path}")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete: {e}")
            return

        index += 1
        self.load_next_image()

    def undo_last(self):
        if not history_stack:
            messagebox.showinfo("Undo", "No previous move to undo.")
            return

        last_dest_path, restore_dir = history_stack.pop()
        filename = os.path.basename(last_dest_path)
        restored_path = os.path.join(restore_dir, filename)

        try:
            shutil.move(last_dest_path, restored_path)
            self.status_text.set(f"↩️ Undid move: {filename} → {restore_dir}")
        except Exception as e:
            messagebox.showerror("Undo Error", f"Failed to undo: {e}")
            return

        if not history_stack:
            self.undo_button.config(state="disabled")


if __name__ == '__main__':
    root = Tk()
    app = ImageSorterGUI(root)
    root.mainloop()

