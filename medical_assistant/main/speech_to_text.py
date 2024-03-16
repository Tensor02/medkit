import tkinter as tk
from tkinter import ttk, filedialog

import self
from ttkthemes import ThemedStyle
import pyaudio
import wave
import os
import threading
from datetime import datetime
import time  # Import time module for time-related operations
import speech_recognition as sr

from medical_assistant.main.entity_recognition_service import highlight_text


class SpeechToTextConverter:
    def __init__(self, root):
        current_timestamp = datetime.now()
        formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H-%M-%S")

        self.root = root
        self.root.title("Speech to Text Converter")

        self.audio_file = self.generate_absolute_path(f"../../data/recorded_conversations/audio/{formatted_timestamp}.wav")
        self.text_file = self.generate_absolute_path(f"../../data/recorded_conversations/text/{formatted_timestamp}.txt")
        self.highlighted_text_file = self.generate_absolute_path(f"../../data/recorded_conversations/text_with_highlights/{formatted_timestamp}.txt")
        self.is_recording = False
        self.start_time = None

        self.recognizer = sr.Recognizer()
        self.microphone = sr.AudioFile(self.audio_file)

        self.start_button = ttk.Button(root, text="Start Recording", command=self.start_recording, style="TButton")
        self.stop_button = ttk.Button(root, text="Stop Recording", command=self.stop_recording, style="TButton")
        self.convert_button = ttk.Button(root, text="Convert", command=self.convert_audio, style="TButton")
        self.text_display = tk.Text(root, height=10, width=40, wrap=tk.WORD)
        self.time_label = tk.Label(root, text="Recording Time: 00:00", font=("Arial", 12))

        self.logo_image = tk.PhotoImage(file='../../data/images/medical_assistant_logo.png')
        self.logo_label = tk.Label(root, image=self.logo_image)

        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10)
        self.start_button.grid(row=1, column=0, pady=10, padx=10)
        self.stop_button.grid(row=1, column=1, pady=10, padx=10)
        self.convert_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10)
        self.time_label.grid(row=3, column=0, columnspan=2, pady=10, padx=10)
        self.text_display.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

        style = ThemedStyle(root)
        style.set_theme("radiance")

    @staticmethod
    def generate_absolute_path(relative_path):
        absolute_path = os.path.abspath(relative_path)
        directory = os.path.dirname(absolute_path)
        if not os.path.exists(directory):
           os.makedirs(directory)
        return absolute_path

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self):
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        audio_dir = os.path.dirname(self.audio_file)
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        while self.is_recording:
            data = stream.read(CHUNK)
            frames.append(data)

            elapsed_time = time.time() - self.start_time
            time_str = time.strftime("%M:%S", time.gmtime(elapsed_time))
            self.time_label.config(text=f"Recording Time: {time_str}")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.audio_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Audio saved as {self.audio_file}")

    def convert_audio(self):
        with self.microphone as source:
            audio_data = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio_data)
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, text)
            self.publish_text(text)
            print('successfully saved speech-to-text results in :', self.text_file)
        except sr.UnknownValueError:
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, "Sorry, could not understand audio.")
        except sr.RequestError as e:
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"Error: {str(e)}")

    def publish_text(self, text):
        with open(self.text_file, "w") as file:
            file.write(text)
        print("Converted text saved to", self.text_file)

        highlighted_text = highlight_text(self.text_file)
        with open(self.highlighted_text_file, "w") as file:
            file.write(highlighted_text)
        print("Highlighted text saved to", self.text_file)


