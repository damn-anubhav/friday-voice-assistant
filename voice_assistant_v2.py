import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
from plyer import notification
import pyautogui
import wikipedia
import pywhatkit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import genai_request as ai
import google.generativeai as genai
import mtranslate
import langdetect

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 195)
engine.runAndWait()

def sanitize_text(text):
    if text is None:
        return ""
    return text.encode("ascii", "ignore").decode("ascii")

def speak(audio, lang="en"):
    if lang != "en":
        try:
            audio = mtranslate.translate(audio, to_language=lang, from_language="en")
        except Exception:
            pass
    engine.say(audio)
    engine.runAndWait()

def command():
    content = " "
    while content == " ":
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        try:
            content = r.recognize_google(audio, language='en-in')
            print(f"You said: {content}")
            try:
                detected_lang = langdetect.detect(content)
            except Exception:
                detected_lang = "en"
            print(f"Detected language: {detected_lang}")
        except Exception as e:
            print("Please try again....")
            return None, "en"
        return content, detected_lang

def main_process():
    friday_chat = []
    while True:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=[
            {"role": "user", "parts": "Hello"},
            {"role": "model", "parts": "Great to meet you. What would you like to know?"},
        ])
        result = command()
        if result is None:
            continue
        request, lang = result
        if request is None:
            continue
        request = request.lower()
        if 'hello' in request:
            speak("Hello, how may I help you?", lang)
        elif 'ask ai' in request:
            req = request.replace("ask ai", "").strip()
            response = ai.get_response(req)
            speak(response, lang)
        elif 'play songs' in request:
            speak("Playing songs...", lang)
            songs = [
                "https://youtu.be/X-0CXsGcW8Y",
                "https://youtu.be/AEIVhBS6baE",
                "https://youtu.be/h6lHUn20J5g"
            ]
            webbrowser.open(random.choice(songs))
        elif 'time' in request:
            now = datetime.datetime.now()
            speak(f"The current time is {now.hour}:{now.minute}", lang)
        elif 'date' in request:
            now = datetime.datetime.now().strftime("%d:%m")
            speak(f"The current date is {now}", lang)
        elif 'new task' in request:
            task = request.replace("new task", "").strip()
            if task:
                with open("todo.txt", "a") as f:
                    f.write(task + "\n")
                speak(f"Added task: {task}", lang)
        elif 'speak task' in request:
            with open("todo.txt", "r") as f:
                speak("Tasks for today are: " + f.read(), lang)
        elif 'show work' in request:
            with open("todo.txt", "r") as f:
                tasks = f.read()
            notification.notify(title="Tasks for Today", message=tasks, timeout=10)
        elif 'open' in request:
            app = request.replace("open", "").strip()
            pyautogui.press("super")
            pyautogui.typewrite(app)
            pyautogui.sleep(0.1)
            pyautogui.press("enter")
        elif 'delete task' in request:
            task = request.replace("delete task", "").strip()
            with open("todo.txt", "r") as f:
                lines = f.readlines()
            with open("todo.txt", "w") as f:
                for line in lines:
                    if task not in line:
                        f.write(line)
            speak("Task deleted successfully", lang)
        elif 'take screenshot' in request:
            now = datetime.datetime.now().strftime("%m-%d_%H-%M")
            filename = f"screenshot_{now}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            speak(f"Screenshot saved as {filename}", lang)
        elif 'friday search' in request or 'search' in request:
            req = request.replace("friday", "").replace("search", "").strip()
            try:
                result = wikipedia.summary(req, sentences=2)
                speak(result, lang)
            except wikipedia.exceptions.PageError:
                speak(f"No matching page found for '{req}'", lang)
        elif 'google' in request:
            req = request.replace("google", "").strip()
            speak(f"Searching for {req}", lang)
            webbrowser.open(f"https://www.google.com/search?q={req}")
        elif 'send email' in request:
            sender_email = "your_email@gmail.com"
            app_password = "your_app_password"
            receiver_email = "receiver_email@gmail.com"
            subject = "Hello from Python"
            body = "This is a test email from the Python voice assistant."
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                speak("Email sent successfully!", lang)
            except Exception as e:
                print(f"Email failed: {e}")
        elif 'clear chat' in request:
            friday_chat.clear()
            speak("Chat history cleared.", lang)
        else:
            req = sanitize_text(request)
            friday_chat.append({"role": "user", "parts": req + " answer very briefly"})
            response = ai.get_response(friday_chat)
            response = sanitize_text(response)
            friday_chat.append({"role": "model", "parts": response})
            speak(response, lang)

if __name__ == "__main__":
    main_process()
