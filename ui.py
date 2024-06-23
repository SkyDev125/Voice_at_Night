import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tts_config import voice
import pystray
from PIL import Image
from pystray import MenuItem as item


# Function to update configurations (placeholder)
def update_config(*args):
    print("Configurations Updated")


def show_window(icon):
    icon.stop()
    root.deiconify()
    root.after(100, lambda: root.focus_force())


def hide_window():
    root.withdraw()
    image = Image.open("resources\images\icon.png")
    menu = (item("Quit", quit_app), item("Show", show_window))
    icon = pystray.Icon("name", image, "Title", menu)
    icon.run()


def quit_app(icon):
    icon.stop()
    root.destroy()


def save_as_default():
    # Show a warning before saving defaults
    response = messagebox.askyesno(
        "Warning", "Are you sure you want to save these settings as defaults?"
    )
    if response:
        # Placeholder for saving logic, e.g., writing to a file
        print("Defaults Saved")
        messagebox.showinfo(
            "Save Defaults", "Defaults have been saved successfully."
        )


# Create the main window
root = tk.Tk()
root.title("TTS and STT Configuration Panel")

# Prevent the window from being resizable
root.resizable(False, False)

# Add padding around the components inside the window
root["padx"] = 10
root["pady"] = 10

# Voice selection
voice_label = ttk.Label(root, text="Select Voice:")
voice_label.grid(column=0, row=0, sticky=tk.W)
voice_var = tk.StringVar()
voice_dropdown = ttk.Combobox(root, textvariable=voice_var, state="readonly")
voice_dropdown["values"] = [voice.name for voice in voice]
voice_dropdown.grid(column=1, row=0)
voice_dropdown.current(0)

# Speech rate
speech_rate_label = ttk.Label(root, text="Speech Rate:")
speech_rate_label.grid(column=0, row=1, sticky=tk.W)
speech_rate_var = tk.IntVar(value=170)
speech_rate_slider = ttk.Scale(
    root, from_=50, to_=300, variable=speech_rate_var, orient=tk.HORIZONTAL
)
speech_rate_slider.grid(column=1, row=1, sticky=tk.EW)

# Volume
volume_label = ttk.Label(root, text="Volume:")
volume_label.grid(column=0, row=2, sticky=tk.W)
volume_var = tk.DoubleVar(value=1)
volume_slider = ttk.Scale(
    root, from_=0.0, to_=1.0, variable=volume_var, orient=tk.HORIZONTAL
)
volume_slider.grid(column=1, row=2, sticky=tk.EW)

# STT Model
model_label = ttk.Label(root, text="STT Model:")
model_label.grid(column=0, row=3, sticky=tk.W)
model_var = tk.StringVar(value="small")
model_entry = ttk.Entry(root, textvariable=model_var)
model_entry.grid(column=1, row=3, sticky=tk.EW)

# English
english_var = tk.BooleanVar(value=True)
english_check = ttk.Checkbutton(
    root, text="Use English Model", variable=english_var
)
english_check.grid(column=0, row=4, columnspan=2)

# Energy Threshold
energy_threshold_label = ttk.Label(root, text="Energy Threshold:")
energy_threshold_label.grid(column=0, row=5, sticky=tk.W)
energy_threshold_var = tk.IntVar(value=1000)
energy_threshold_entry = ttk.Entry(root, textvariable=energy_threshold_var)
energy_threshold_entry.grid(column=1, row=5, sticky=tk.EW)

# Record Timeout
record_timeout_label = ttk.Label(root, text="Record Timeout (s):")
record_timeout_label.grid(column=0, row=6, sticky=tk.W)
record_timeout_var = tk.IntVar(value=2)
record_timeout_entry = ttk.Entry(root, textvariable=record_timeout_var)
record_timeout_entry.grid(column=1, row=6, sticky=tk.EW)

# Phrase Timeout
phrase_timeout_label = ttk.Label(root, text="Phrase Timeout (s):")
phrase_timeout_label.grid(column=0, row=7, sticky=tk.W)
phrase_timeout_var = tk.IntVar(value=3)
phrase_timeout_entry = ttk.Entry(root, textvariable=phrase_timeout_var)
phrase_timeout_entry.grid(column=1, row=7, sticky=tk.EW)

# Save Button
save_button = ttk.Button(root, text="Run", command=update_config)
# Adjusted to be in the center-left position with padding for spacing
save_button.grid(column=0, row=8, padx=(10, 5), pady=10)

# New Button for Saving Defaults
save_defaults_button = ttk.Button(
    root, text="Set New Defaults", command=save_as_default
)
# Adjusted to be in the center-right position with padding for spacing
save_defaults_button.grid(column=1, row=8, padx=(5, 10), pady=10)

# Modify the application to minimize to system tray on close
root.protocol("WM_DELETE_WINDOW", hide_window)

# Run the application
root.mainloop()
