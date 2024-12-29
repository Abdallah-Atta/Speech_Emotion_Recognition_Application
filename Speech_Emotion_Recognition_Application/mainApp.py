import flet as ft
import sounddevice as sd
import wavio
import os
import uuid
import datetime
import requests
from Backend import predict
from flet.core.colors import colors
from pygments.styles.dracula import background
import joblib
from tensorflow.keras.models import load_model
import joblib
from conn import *
import pygame
import requests
import tempfile
from playsound import playsound
from For_prediction import predict_emotion


BACKEND_URL = "http://127.0.0.1:5000"  # Flask backend URL

# Function to record audio
def record_audio(file_path, duration=5, sample_rate=44100):
    try:
        # Record audio for the specified duration
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        wavio.write(file_path, recording, sample_rate, sampwidth=2)  # Save as WAV file
        return True, "Recording successful!"

    except Exception as e:
        return False, f"Recording failed: {str(e)}"

import secrets

def play_recorded(url):
    """
    Function to play an audio recording directly in the app.

    Args:
        url (str): The cloud link or URL of the audio recording.
    """
    if not url:
        print("Error: No valid URL provided!")
        return

    try:
        # Download the audio file
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request fails

        # Save the file to a temporary location
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(response.content)
            temp_file_path = temp_audio.name

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load and play the audio file
        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()

        print(f"Playing audio from: {url}")

        while pygame.mixer.music.get_busy():
            pass

        print(f"Playing audio from: {url}")
        page.update()

    except Exception as e:
        print(f"Error playing audio: {e}")


def main(page: ft.Page):
    page.title = "Emotion Recognizer"
    page.window_width = 350
    page.window_height = 700

    image_folder = "images"
    page.assets_dir = os.path.join(os.getcwd(), image_folder)

    # Global variables for the login fields
    global username_field, password_field, error_message

    username_field = ft.TextField(label="Username")
    password_field = ft.TextField(label="Password", password=True,can_reveal_password=True)
    error_message = ft.Text(value="", color=ft.colors.RED)

    # Path to the logo image
    logo_image_path = r"https://th.bing.com/th/id/OIP.Wp57o0ezC6TX6XbkVpNPHwHaHa?rs=1&pid=ImgDetMain --"

    about_photo = r"D:\AI\deep_learning\Final_project\myApp\Screenshot 2024-12-08 212801.png"
    # model_accuracy_photo=about_photo = r"https://th.bing.com/th/id/OIP.Wp57o0ezC6TX6XbkVpNPHwHaHa?rs=1&pid=ImgDetMain --"
    recordings_folder = "D:\AI\deep_learning\Final_project\myApp\Recordes"  # Path to save recorded audio


    image_folder = os.path.join(os.getcwd(), image_folder)  # Ensure this folder exists
    photo1 = os.path.join(image_folder, "image1.png")
    image="https://file.io/D53csXZz7OTt"
    # Ensure the recordings folder exists
    if not os.path.exists(recordings_folder):
        os.makedirs(recordings_folder)

    # Generate a unique filename for each recording
    def generate_filename():
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]  # Short UUID
        filename = f"recording_{timestamp}_{unique_id}.wav"
        return os.path.join(recordings_folder, filename)

    current_user_id = None

    def open_main_app(current_user_id):
        print(current_user_id)
        global message_box, dialog
        message_box = ft.Column(
            controls=[],
            scroll="auto",
            expand=True,
            height=300,  # Adjust the height to fit your needs

        )

        # === Animation Effects ===
        fade_in = ft.Animation(500, "ease_in_out")  # Smooth fade-in
        fade_out = ft.Animation(500, "ease_in_out")  # Smooth fade-out

        def toggle_pulse_effect(base_mode=False):
            if base_mode:
                # Reset to base mode
                pulse_circle.scale = ft.Scale(1)
                pulse_circle.opacity = 1
                mic_button.icon_color = ft.colors.RED_ACCENT
                mic_button.name = ft.icons.MIC
            else:
                # Toggle active recording state
                pulse_circle.scale = ft.Scale(0.8)#1.2
                pulse_circle.opacity = 0.9
                mic_button.icon_color = ft.colors.GREEN
                mic_button.name = ft.icons.MIC_NONE
            page.update()

        def on_mic_click(e):

            toggle_pulse_effect()
            audio_path = generate_filename()
            global mic_path
            mic_path = audio_path
            duration = 5  # Record for 3 seconds

            result, message = record_audio(audio_path, duration=duration)

            if result:
                # Save the record to the database
                toggle_pulse_effect(base_mode=True)
                success = save_record(current_user_id, audio_path)

                if success:
                    output.value = f"Audio recorded and uploaded successfully! File saved at {audio_path}"
                else:
                    output.value = "Recording saved locally, but failed to save in the database."
            else:
                output.value = message

            page.update()

        def show_photo():

            dialog = ft.AlertDialog(
                content=ft.Image(src=image_url, width=600, height=600),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog())],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        def close_dialog():

            page.dialog.open = False
            page.update()

        def logout():
            page.controls.clear()
            render_login_page()
            page.update()

        # AppBar with the image as the logo
        page.appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Image(
                    src=logo_image_path,
                    width=40,  # Adjust logo size
                    height=40,
                    fit=ft.ImageFit.CONTAIN,
                ),
                width=50,
                height=50,
            ),
            leading_width=60,
            title=ft.Row(
                            controls=[
                                ft.Text("Emotion Recognizer", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Icon(ft.icons.MIC, size=24, color=ft.colors.WHITE),  # Add microphone icon beside the title
                            ],
                            spacing=10,  # Space between text and icon
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
            center_title=True,
            bgcolor=ft.colors.BLUE_ACCENT_400,
        )

        # Main content 
        output = ft.Text(
            value="Click the microphone to record audio or upload audio file",
            color=ft.colors.BLUE_GREY_400,
            size=18,
            weight=ft.FontWeight.NORMAL,
        )

        #//////////////////////////////////////////////////////////////////////////////
        # Function to handle file picking
        result_text = ft.Text("")

        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                # Display the full path of the selected file
                selected_file_path = e.files[0].path  # Get the full file path
                selected_file.value = f"Selected file: {e.files[0].name}\nPath: {selected_file_path}"
                selected_file.update()

                # Pass the file object to upload
                upload_file(e.files[0])
            else:
                selected_file.value = "No file selected."
                selected_file.update()

        def upload_file(file):
            global upload_path

            if not file:
                selected_file.value = "No file selected."
                selected_file.update()
                return

            try:
                # Handle the FilePickerFile object
                if file.path:  # If the file has a valid path
                    upload_path = file.path
                    with open(file.path, "rb") as f:
                        file_content = f.read()
                else:  # If no path is provided, use file.bytes
                    upload_path = file.name
                    file_content = file.bytes

                # Prepare files and data for the request
                files = {"file": (file.name, file_content)}
                data = {"user_id": current_user_id}  # Include user ID with the request

                # Send the request to the backend
                response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)

                # Handle the response
                if response.status_code == 200:
                    selected_file.value = f"File uploaded successfully: {file.name}"
                else:
                    error_message = response.json().get("error", "Unknown error")
                    selected_file.value = f"Error: {error_message}"
                selected_file.update()
            except Exception as ex:
                print(f"Exception occurred: {str(ex)}")
                result_text.value = f"Error: {str(ex)}"
                page.update()

        # File picker instance
        file_picker = ft.FilePicker(on_result=lambda e: upload_file(e.files[0]))

        # Text to display selected file

        selected_file = ft.Text(value="No file selected.", size=16, color="")

        # def on_predict(e=None):
        #     """
        #             Handles the prediction process by accepting an audio file path,
        #             sending it to the backend, and displaying the prediction result in a message box.
        #                 """
        #     global mic_path
        #     global upload_path
        #
        #     # Check if either upload_path or mic_path exists and is valid
        #     if 'upload_path' in globals() and upload_path:
        #         path = upload_path
        #         upload_path = None  # Clear after using
        #     elif 'mic_path' in globals() and mic_path:
        #         path = mic_path
        #         mic_path = None  # Clear after using
        #     else:
        #         # Handle case where neither is available
        #         print("No audio file selected.")
        #         show_result("No audio file provided.")
        #         return
        #
        #     try:
        #             # Call the `predict_emotion` function from your test model
        #         scaler = joblib.load("scaler.pkl")
        #         encoder = joblib.load("encoder.pkl")
        #         trained_model = load_model('speech_emotion_cnn_model.keras')
        #
        #         predicted_emotion = predict_emotion(
        #             path, trained_model, scaler, encoder
        #         )
        #
        #         # Display the prediction result
        #         show_result(f"The predicted emotion is: {predicted_emotion}")
        #     except Exception as ex:
        #         print(f"Exception occurred: {str(ex)}")
        #         show_result(f"Error: {str(ex)}")
        def on_predict(e=None):
            """
            Handles the prediction process by accepting an audio file path,
            sending it to the backend, and displaying the prediction result in a message box.
            """
            global mic_path
            global upload_path

            # Check if either upload_path or mic_path exists and is valid
            if 'upload_path' in globals() and upload_path:
                path = upload_path
                upload_path = None  # Clear after using
            elif 'mic_path' in globals() and mic_path:
                path = mic_path
                mic_path = None  # Clear after using
            else:
                # Handle case where neither is available
                print("No audio file selected.")
                show_result("No audio file provided.")
                return

            try:
                # Send the audio file to the backend for prediction
                with open(path, 'rb') as f:
                    files = {'file': (path, f)}
                    response = requests.post("http://127.0.0.1:5000/predict", files=files,
                                             timeout=60)  # 60 seconds timeout

                # Check the response from the server
                if response.status_code == 200:
                    # Assuming the backend sends back the prediction in JSON
                    prediction = response.json()
                    predicted_emotion = prediction.get("prediction", "Unknown")
                    show_result(f"The predicted emotion is: {predicted_emotion}")
                else:
                    # Handle the error if the backend responds with an error
                    error_message = response.json().get("error", "Unknown error")
                    show_result(f"Error: {error_message}")
            except Exception as ex:
                print(f"Exception occurred: {str(ex)}")
                show_result(f"Error: {str(ex)}")
        def show_result(message):
            """
            Shows the result message in an alert dialog.
            """
            result_dialog = ft.AlertDialog(
                title=ft.Text("Prediction Result"),  # Wrap title in ft.Text
                content=ft.Text(message),
                actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(result_dialog))],
            )
            page.add(result_dialog)
            result_dialog.open = True  # Set open to True to display the dialog
            page.update()

        def close_dialog(dialog):
            """
            Close the dialog when the close button is clicked.
            """
            dialog.open = False  # Set open to False to close the dialog
            page.update()

        predict_button = ft.ElevatedButton(
            "Predict",
            on_click=on_predict,  # Bind the button click to the on_predict function
        )
        # Icon button for file picker
        upload_button = ft.IconButton(
            icon=ft.icons.UPLOAD_FILE,
            tooltip="Upload Audio File",
            icon_color="blue",
            on_click=lambda _: file_picker.pick_files(
                allow_multiple=False,  # Only allow one file
                allowed_extensions=["mp3", "wav"],  # Restrict to audio files
            ),
        )

        # Add components to the page

        pb = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text=" show info about model ",icon=ft.Icons.DOOR_BACK_DOOR_OUTLINED),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(icon=ft.Icons.POWER_INPUT, text="Check power"),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HOURGLASS_TOP_OUTLINED),
                            ft.Text("Item with a custom content"),
                        ]
                    ),
                    on_click=lambda _: show_photo(),
                ),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(icon=ft.icons.HISTORY, text="History",on_click=show_history),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.HOURGLASS_TOP_OUTLINED),
                            ft.Text("Show acuracy "),
                        ]
                    ),

                    on_click=lambda _: show_photo(),
                ),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(icon=ft.icons.EXIT_TO_APP, text="Logout", on_click=lambda e: logout()),
                ft.PopupMenuItem(),

            ]
        )

        # Clear the page and add main app content
        page.controls.clear()

        page.add(pb)
        # //////////////////////////////////////////////////////////////////////////////

       # add the output text to the app
        page.add(
            ft.Container(
                content=output,
                expand=True,
                alignment=ft.alignment.center,
            )
        )
       # add the upload buttom and slected file text to the app
        page.add(
            ft.Row(
                controls=[
                    upload_button,
                    selected_file,
                ],
                alignment= ft.MainAxisAlignment.START,
            ),
            file_picker,
        )




        mic_button = ft.IconButton(
            icon=ft.icons.MIC,
            icon_size=40,
            tooltip="Record Audio",
            on_click=on_mic_click,  # Attach the microphone action
            icon_color=ft.colors.RED_ACCENT,
            bgcolor=ft.colors.WHITE,
            width=60,
            height=60,

        )
        page.add(
            ft.Column(
                alignment=ft.MainAxisAlignment.END,  # Align the content to the bottom
                controls=[  # Use `controls` instead of `children`
                    ft.Container(
                        content=predict_button,
                        alignment=ft.alignment.center,  # Center the button horizontally
                        padding=ft.Padding(top=2, left=0, right=0, bottom=0),  # Add space from the top
                    )
                ]
            )
        )
        pulse_circle = ft.Container(
            content=mic_button,
            width=60,
            height=60,
            bgcolor=ft.colors.WHITE,
            border_radius=30,
            alignment=ft.alignment.center,
            animate_scale=ft.Animation(600, "ease_in_out"),
            animate_opacity=ft.Animation(600, "ease_in_out"),
        )

        # Add the mic button to the bottom-left of the page using alignment
        page.add(
            ft.Container(
                content=pulse_circle,
                alignment=ft.alignment.bottom_right,
                padding=20  # Add some space around the button
            )

        )


        # Create the dialog
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                [
                    ft.Text("Recordes", size=24, weight="bold"),
                    message_box,  # Add the message box inside the dialog
                    ft.TextButton(
                        text="Close",
                        on_click=close_message_box
                    )
                ],
                expand=True
            ),
            actions_alignment="center"
        )
        page.dialog = dialog



    def show_history(e):
        print("show_history function triggered")

        # Fetch the user's recordings from the Flask backend
        try:
            response = requests.get(f"{BACKEND_URL}/recordings/{current_user_id}")
            if response.status_code == 200:
                records = response.json().get("recordings", [])
            else:
                records = []
                print("Error fetching records:", response.json().get('error'))
        except Exception as ex:
            print(f"Error while fetching records: {str(ex)}")
            records = []

        # Clear the existing message box content
        message_box.controls.clear()

        # If no records, show a message
        if not records:
            message_box.controls.append(ft.Text("No recordings found!", size=18, color=ft.colors.RED))
        else:
            for record in records:
                filename = record.get('file_path')
                message_box.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"Recorded at: {record['timestamp']}", size=16, color=ft.colors.BLUE),
                                ft.TextButton(
                                    text="Play Recording",
                                    on_click=lambda e, filename=filename: play_recorded(filename)
                                ),
                                ft.Divider(height=1, color=ft.colors.GREY)
                            ]
                        ),
                        padding=10
                    )
                )

        # Show the dialog
        dialog.open = True
        page.update()

    def close_message_box(e):
        dialog.open = False
        page.update()

    # Only update the message box, not the whole page

    def play_recorded(filename):
        try:
            # Replace 'source' with 'src'
            audio_player = ft.Audio(src=filename, autoplay=True)
            page.overlay.append(audio_player)
            page.update()
            print(f"Playing recording: {filename}")
        except Exception as e:
            print(f"Error while playing the recording: {e}")

    def handle_login(e):
        username = username_field.value
        password = password_field.value
        user_id = authenticate_user(username, password)
        if user_id:
            nonlocal current_user_id
            current_user_id = user_id
            open_main_app(current_user_id)
        else:
            error_message.value = "Invalid username or password!"
            page.update()

    def render_login_page(e=None):
        page.controls.clear() # Clear existing content before rendering the login page

        signup_redirect_button = ft.TextButton("Sign Up", on_click=show_signup_page)

        login_button = ft.ElevatedButton("Login", on_click=handle_login)

        page.add(
            ft.Column(
                [
                    ft.Text("Login Page", size=24, weight=ft.FontWeight.BOLD),
                    username_field,
                    password_field,
                    login_button,
                    error_message,
                    signup_redirect_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        )

    def handle_signup(e):

            username = signup_username_field.value.strip()
            password = signup_password_field.value.strip()

            if not username or not password:
                signup_message.value = "Username and password cannot be empty!"
                page.update()
                return

            try:
                # Attempt to add the user
                success = add_user(username, password)

                if success:
                    signup_message.value = "Signup successful! Please log in."
                    signup_message.color = ft.colors.GREEN
                else:
                    signup_message.value = "the user is already exits in the system  "  # Display the error message if username already exists
                    signup_message.color = ft.colors.RED

            except Exception as e:
                signup_message.value = f"Error: {str(e)}"
                signup_message.color = ft.colors.RED

            page.update()

    def show_signup_page(e):
            """Display the signup page."""
            page.clean()

            global signup_username_field, signup_password_field, signup_message

            signup_username_field = ft.TextField(label="Username", autofocus=True)
            signup_password_field = ft.TextField(label="Password", password=True, can_reveal_password=True)
            signup_button = ft.ElevatedButton("Sign Up", on_click=handle_signup)
            signup_message = ft.Text(value=" ", color=ft.colors.RED)

            back_to_login_button = ft.TextButton("Back to Login", on_click=render_login_page)

            page.add(
                ft.Column(
                    [
                        ft.Text("Sign Up", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                        signup_username_field,
                        signup_password_field,
                        signup_button,
                        signup_message,
                        back_to_login_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                )
            )

            page.update()

    render_login_page()
    page.update()
if __name__ == "__main__":
    ft.app(target=main, port=8000)
