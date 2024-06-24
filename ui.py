import ast
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pystray
from PIL import Image
from pystray import MenuItem as item
import inspect
import config
import speech_to_text as stt
import threading
import globals
import sv_ttk

# ==================================================
# Helper Functions
# ==================================================


def find_key(d, value):
    return next((k for k, v in d.items() if v == value), None)


# ==================================================
# STT Thread Management
# ==================================================


def start(
    voices,
    voice_var,
    speech_rate_var,
    volume_var,
    model_var,
    english_var,
    energy_threshold_var,
    record_timeout_var,
    output_devices,
    output_device_var,
):
    def stt_main_thread():
        stt.stt_main(
            voices[voice_var.get()],
            speech_rate_var.get(),
            volume_var.get(),
            globals.whisper_model[model_var.get()],
            english_var.get(),
            energy_threshold_var.get(),
            record_timeout_var.get(),
            output_devices[output_device_var.get()],
        )

    globals.stt_running = True
    globals.stt_thread = threading.Thread(target=stt_main_thread)
    globals.stt_thread.start()


def stop():
    globals.stt_running = False
    if globals.stt_thread:
        globals.stt_thread.join()

# ==================================================
# Default config update functions
# ==================================================


def save_as_default(
    voices,
    voice_var,
    speech_rate_var,
    volume_var,
    model_var,
    english_var,
    energy_threshold_var,
    record_timeout_var,
    output_devices,
    output_device_var,
):
    # Show a warning before saving defaults
    response = messagebox.askyesno(
        "Warning", "Are you sure you want to save these settings as defaults?"
    )
    if response:
        update_config_value("voice_id", voices[voice_var.get()])
        update_config_value("speech_rate", speech_rate_var.get())
        update_config_value("volume", volume_var.get())
        update_config_value("model", globals.whisper_model[model_var.get()])
        update_config_value("english", english_var.get())
        update_config_value("energy_threshold", energy_threshold_var.get())
        update_config_value("record_timeout", record_timeout_var.get())
        update_config_value(
            "output_device_id", output_devices[output_device_var.get()]
        )
        messagebox.showinfo(
            "Save Defaults", "Defaults have been saved successfully."
        )


def update_config_value(target_id, new_value):
    config_file_path = inspect.getfile(config)
    with open(config_file_path, "r+") as file:
        content = file.read()
        parsed = ast.parse(content)
        for node in ast.walk(parsed):
            if (
                isinstance(node, ast.Assign)
                and node.targets[0].id == target_id
            ):
                node.value = ast.Constant(value=new_value)
        new_content = ast.unparse(parsed)
        file.seek(0)
        file.write(new_content)
        file.truncate()


# ==================================================
# System tray management functions
# ==================================================


def show_window(icon, root):
    icon.stop()
    root.deiconify()
    root.after(100, lambda: root.focus_force())


from tkinter import messagebox  # Import messagebox for the confirmation dialog


def hide_window(root):
    # Ask the user if they want to minimize to tray
    if messagebox.askyesno(
        "Minimize to Tray",
        "Do you want to minimize the application to the system tray?",
    ):
        root.withdraw()
        image = Image.open(
            "resources\\images\\icon.ico"
        )  # Corrected the path for consistency
        menu = (
            item("Quit", lambda: quit_app(icon, root)),
            item("Show", lambda: show_window(icon, root)),
        )
        icon = pystray.Icon("name", image, "Title", menu)
        icon.run()
    else:
        quit_app(None, root)


def quit_app(icon, root):
    stop()
    root.destroy()
    if icon:
        icon.stop()


# ==================================================
# UI Creation
# ==================================================


def create_UI():
    # Create the main window
    root = tk.Tk()
    root.title("TTS and STT Configuration Panel")
    root.iconbitmap("resources\images\icon.ico")
    sv_ttk.set_theme("dark")

    # Prevent the window from being resizable
    # root.resizable(False, False)

    # Add padding around the components inside the window
    root["padx"] = 10
    root["pady"] = 10

    # Configure column 1 to expand
    root.grid_columnconfigure(1, weight=1)

    # Voice selection
    voices = stt.get_tts_voices()
    voice_label = ttk.Label(root, text="Select Voice:")
    voice_label.grid(column=0, row=0, sticky=tk.W)
    voice_var = tk.StringVar(value=find_key(voices, config.voice_id))
    voice_dropdown = ttk.Combobox(
        root, textvariable=voice_var, state="readonly"
    )
    voice_dropdown["values"] = list(voices.keys())
    voice_dropdown.grid(column=1, row=0, sticky="ew")

    # Speech rate
    speech_rate_label = ttk.Label(root, text="Speech Rate:")
    speech_rate_label.grid(column=0, row=1, sticky=tk.W)
    speech_rate_var = tk.IntVar(value=config.speech_rate)
    speech_rate_slider = ttk.Scale(
        root, from_=50, to_=300, variable=speech_rate_var, orient=tk.HORIZONTAL
    )
    speech_rate_slider.grid(column=1, row=1, sticky="ew")

    # Volume
    volume_label = ttk.Label(root, text="Volume:")
    volume_label.grid(column=0, row=2, sticky=tk.W)
    volume_var = tk.DoubleVar(value=config.volume)
    volume_slider = ttk.Scale(
        root, from_=0.0, to_=1.0, variable=volume_var, orient=tk.HORIZONTAL
    )
    volume_slider.grid(column=1, row=2, sticky="ew")

    # STT Model
    model_label = ttk.Label(root, text="STT Model:")
    model_label.grid(column=0, row=3, sticky=tk.W)
    model_var = tk.StringVar(
        value=find_key(globals.whisper_model, config.model)
    )
    model_combobox = ttk.Combobox(
        root, textvariable=model_var, state="readonly"
    )
    model_combobox["values"] = list(globals.whisper_model.keys())
    model_combobox.grid(column=1, row=3, sticky="ew")

    # English
    english_var = tk.BooleanVar(value=True)
    english_check = ttk.Checkbutton(
        root, text="Use English Model", variable=english_var
    )
    english_check.grid(column=0, row=4, columnspan=2, sticky="ew")

    # Energy Threshold
    energy_threshold_label = ttk.Label(root, text="Energy Threshold:")
    energy_threshold_label.grid(column=0, row=5, sticky=tk.W)
    energy_threshold_var = tk.IntVar(value=config.energy_threshold)
    energy_threshold_entry = ttk.Entry(root, textvariable=energy_threshold_var)
    energy_threshold_entry.grid(column=1, row=5, sticky="ew")

    # Record Timeout
    record_timeout_label = ttk.Label(root, text="Record Timeout (s):")
    record_timeout_label.grid(column=0, row=6, sticky=tk.W)
    record_timeout_var = tk.IntVar(value=config.record_timeout)
    record_timeout_entry = ttk.Entry(root, textvariable=record_timeout_var)
    record_timeout_entry.grid(column=1, row=6, sticky="ew")

    # Output Device Selection
    output_devices_label = ttk.Label(root, text="Select Output Device:")
    output_devices_label.grid(column=0, row=8, sticky=tk.W)
    output_devices = stt.get_output_devices()
    output_device_var = tk.StringVar(
        value=find_key(output_devices, config.output_device_id)
    )
    output_device_combobox = ttk.Combobox(
        root, textvariable=output_device_var, state="readonly"
    )
    output_device_combobox["values"] = list(output_devices.keys())
    output_device_combobox.grid(column=1, row=8, sticky="ew")

    def toggle_stt():
        if not globals.stt_running:
            start(
                voices,
                voice_var,
                speech_rate_var,
                volume_var,
                model_var,
                english_var,
                energy_threshold_var,
                record_timeout_var,
                output_devices,
                output_device_var,
            )
            status_button.config(text="Stop", style="On.TButton")
        else:
            stop()
            status_button.config(text="Start", style="TButton")

    # Create styles for the button
    style = ttk.Style()
    style.configure("On.TButton", background="red")

    # Status Button
    status_button = ttk.Button(
        root,
        text="Start",
        command=toggle_stt,  # Changed to toggle_stt
        style="TButton",
    )
    # Adjusted to be in the center-left position with padding for spacing
    status_button.grid(column=0, row=9, padx=(10, 5), pady=10)

    # New Button for Saving Defaults
    save_defaults_button = ttk.Button(
        root,
        text="Set New Defaults",
        command=lambda: save_as_default(
            voices,
            voice_var,
            speech_rate_var,
            volume_var,
            model_var,
            english_var,
            energy_threshold_var,
            record_timeout_var,
            output_devices,
            output_device_var,
        ),
    )
    # Adjusted to be in the center-right position with padding for spacing
    save_defaults_button.grid(column=1, row=9, padx=(5, 10), pady=10)

    # Modify the application to minimize to system tray on close
    root.protocol("WM_DELETE_WINDOW", lambda: hide_window(root))

    # Run the application
    root.mainloop()


# ==================================================
# Main
# ==================================================


if __name__ == "__main__":
    create_UI()
