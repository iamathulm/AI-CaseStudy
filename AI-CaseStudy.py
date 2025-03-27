import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import speech_recognition as sr
import pyttsx3
import os
import threading


class SpeechConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Speech Conversion Toolkit")
        master.geometry("600x700")
        master.configure(bg='#f0f0f0')
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Text to Speech Conversion",
                 font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=(10, 5))
        self.tts_input_label = tk.Label(self.master, text="Enter Text to Convert:", bg='#f0f0f0')
        self.tts_input_label.pack(pady=(5, 0))
        self.tts_input = scrolledtext.ScrolledText(self.master, height=5, width=70, wrap=tk.WORD)
        self.tts_input.pack(pady=5)

        tts_frame = tk.Frame(self.master, bg='#f0f0f0')
        tts_frame.pack(pady=5)
        tk.Button(tts_frame, text="Convert to Speech", command=self.text_to_speech,
                  bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(tts_frame, text="Save Audio", command=self.save_speech,
                  bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Label(self.master, text="Speech to Text Conversion",
                 font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=(10, 5))

        stt_frame = tk.Frame(self.master, bg='#f0f0f0')
        stt_frame.pack(pady=5)
        tk.Button(stt_frame, text="Convert from Audio File", command=self.speech_to_text_file,
                  bg='#FF9800', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(stt_frame, text="Record from Microphone", command=self.speech_to_text_mic,
                  bg='#9C27B0', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Label(self.master, text="Conversion Results:", bg='#f0f0f0').pack(pady=(10, 0))

        self.results_display = scrolledtext.ScrolledText(self.master, height=10, width=70, wrap=tk.WORD)
        self.results_display.pack(pady=5)
        self.results_display.config(state=tk.DISABLED)

    def text_to_speech(self):
        text = self.tts_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to convert.")
            return

        try:
            voices = self.tts_engine.getProperty('voices')
            self.tts_engine.setProperty('rate', 150)  
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

            self.update_results(f"Text-to-Speech conversion completed.\nText spoken: {text}")
        except Exception as e:
            messagebox.showerror("Error", f"Text-to-Speech conversion failed: {str(e)}")

    def save_speech(self):
        """Save text to speech as audio file"""
        text = self.tts_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to save.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
            )

            if file_path:
                self.tts_engine.save_to_file(text, file_path)
                self.tts_engine.runAndWait()
                self.update_results(f"Speech saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save speech: {str(e)}")

    def speech_to_text_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.ogg"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return
        threading.Thread(target=self._process_audio_file, args=(file_path,), daemon=True).start()

    def _process_audio_file(self, file_path):
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio)
            self.master.after(0, self.update_results, f"Transcribed Text:\n{text}")
        except sr.UnknownValueError:
            self.master.after(0, messagebox.showinfo, "Result", "Could not understand the audio")
        except sr.RequestError as e:
            self.master.after(0, messagebox.showerror, "Error", f"Recognition service error: {e}")
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", f"Audio processing failed: {str(e)}")

    def speech_to_text_mic(self):
        threading.Thread(target=self._record_from_mic, daemon=True).start()
        self.recording_window = tk.Toplevel(self.master)
        self.recording_window.title("Recording")
        self.recording_window.geometry("300x100")
        tk.Label(self.recording_window, text="Listening... Speak now!", font=('Arial', 12)).pack(expand=True)

    def _record_from_mic(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source)
            if hasattr(self, 'recording_window'):
                self.recording_window.destroy()

            text = self.recognizer.recognize_google(audio)
            self.master.after(0, self.update_results, f"Transcribed Text:\n{text}")
        except sr.UnknownValueError:
            self.master.after(0, messagebox.showinfo, "Result", "Could not understand the audio")
        except sr.RequestError as e:
            self.master.after(0, messagebox.showerror, "Error", f"Recognition service error: {e}")
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", f"Microphone recording failed: {str(e)}")

    def update_results(self, message):
        """Update results display"""
        self.results_display.config(state=tk.NORMAL)
        self.results_display.delete('1.0', tk.END)
        self.results_display.insert(tk.END, message)
        self.results_display.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechConverterGUI(root)
    root.mainloop()
