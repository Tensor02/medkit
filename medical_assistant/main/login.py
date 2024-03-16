import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import logging
import configparser

from medical_assistant.main.speech_to_text import SpeechToTextConverter


# Create a dictionary to store valid username-password pairs (you can replace this with a database)
class Runner:
    def __init__(self):
        self.config = configparser.ConfigParser()
        # fetching valid users from config.ini
        self.config.read('../config/config.ini')
        self.valid_users = self.config['valid_users']

        self.stt = None

    # Function to check login credentials
    def check_login(self):
        username = username_entry.get()
        password = password_entry.get()

        if username in self.valid_users and self.config.get('valid_users', username) == password:
            # Close the login window
            login_window.destroy()

            # Open the data entry form
            self.open_record_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_record_window(self):
        root = tk.Tk()
        self.stt = SpeechToTextConverter(root)
        root.mainloop()


if __name__ == "__main__":
    runner_obj = Runner()

    # Create the main window for login
    logging.info("Validating User login...")
    login_window = tk.Tk()
    login_window.title("Login")

    # Create labels and entry fields for login
    username_label = tk.Label(login_window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")  # Show asterisks for password
    password_entry.pack()

    # Create a login button
    login_button = tk.Button(login_window, text="Login", command=runner_obj.check_login)
    login_button.pack()

    # Start the tkinter main loop for the login window
    login_window.mainloop()
    os.system("exit 0")
