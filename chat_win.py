import os
import sqlite3
import requests
import pyautogui
import time
import pygame
import pyttsx3 as pt
import pandas as pd
import platform
import win32api
from os import system

class ChatBot:
    def __init__(self):
        self.conn_chat_history = sqlite3.connect('chat_history.db')
        self.conn_chat_logs = sqlite3.connect('chat_logs.db')
        self.conn_code_history = sqlite3.connect('code_history.db')
        self.create_table()

    def create_table(self):
        cursor_chat_history = self.conn_chat_history.cursor()
        cursor_chat_history.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                                        id INTEGER PRIMARY KEY,
                                        user_input TEXT,
                                        bot_response TEXT
                                      )''')
        self.conn_chat_history.commit()

        cursor_chat_logs = self.conn_chat_logs.cursor()
        cursor_chat_logs.execute('''CREATE TABLE IF NOT EXISTS chat_logs (
                                        id INTEGER PRIMARY KEY,
                                        user_input TEXT,
                                        bot_response TEXT
                                      )''')
        self.conn_chat_logs.commit()

        cursor_code_history = self.conn_code_history.cursor()
        cursor_code_history.execute('''CREATE TABLE IF NOT EXISTS code_history (
                                        id INTEGER PRIMARY KEY,
                                        code TEXT,
                                        user_input TEXT,
                                        bot_response TEXT
                                      )''')
        self.conn_code_history.commit()

    def record_chat(self, user_input, bot_response):
        cursor_chat_history = self.conn_chat_history.cursor()
        cursor_chat_history.execute('''INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)''', (user_input, bot_response))
        self.conn_chat_history.commit()

        cursor_chat_logs = self.conn_chat_logs.cursor()
        cursor_chat_logs.execute('''INSERT INTO chat_logs (user_input, bot_response) VALUES (?, ?)''', (user_input, bot_response))
        self.conn_chat_logs.commit()

    def record_code(self, code, user_input, bot_response):
        cursor_code_history = self.conn_code_history.cursor()
        cursor_code_history.execute('''INSERT INTO code_history (code, user_input, bot_response) VALUES (?, ?, ?)''', (code, user_input, bot_response))
        self.conn_code_history.commit()

    def export_to_csv(self, filename="chat_history.csv"):
        df = pd.read_sql_query("SELECT * FROM chat_history", self.conn_chat_history)
        df.to_csv(filename, index=False)
        print(f"Chat history exported to {filename}")

    def list_chat(self):
        cursor_chat_history = self.conn_chat_history.cursor()
        cursor_chat_history.execute('''SELECT * FROM chat_history''')
        rows = cursor_chat_history.fetchall()
        print("Chat History:")
        for row in rows:
            print(f"User: {row[1]}")
            print(f"Bot: {row[2]}")

        cursor_chat_logs = self.conn_chat_logs.cursor()
        cursor_chat_logs.execute('''SELECT * FROM chat_logs''')
        rows = cursor_chat_logs.fetchall()
        print("\nChat Logs:")
        for row in rows:
            print(f"User: {row[1]}")
            print(f"Bot: {row[2]}")

    def shutdown_system(self):
        # Open the start menu
        pyautogui.hotkey('winleft')
        time.sleep(1)  # Wait for 1 second

        # Type the shutdown command
        pyautogui.write('shutdown /s /t 1')
        pyautogui.press('enter')

    def play_music(self, music_file_path):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(music_file_path)
        pygame.mixer.music.play()

    def get_chat_response(self, user_input):
        se = requests.Session()
        url = f"http://www.mahrez.iapp.ir/Gpt/?text={user_input}"
        try:
            response = se.get(url)
            response.raise_for_status()
            bot_response = response.json()["message"]
            self.record_chat(user_input, bot_response)
            return bot_response
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {str(e)}"

    def main(self):
        # Read the code from the file
        with open(__file__, 'r') as file:
            code_content = file.read()

        while True:
            user_input = input("You: ")

            if user_input.lower() == "exit":
                print("Goodbye")
                pt.speak("Goodbye")
                break

            elif user_input.lower() == "خاموش":
                self.shutdown_system()
                print("Goodbye!")
                break

            elif user_input.lower() == "play music" or user_input == "پخش اهنگ" or user_input=="play_music":
                pt.speak("Please enter the path of the audio file:")
                music_file_path = input("Please enter the path of the audio file:")
                if os.path.exists(music_file_path):
                    self.play_music(music_file_path)
                    print("The audio file is playing.")
                else:
                    print('The imported file does not exist.')
                continue
            elif user_input=="system" or user_input =="مشخصات سیستم" or user_input =="مشخصات":
                print(platform.uname())
                pt.speak(platform.uname())
            elif user_input =="command" or user_input=="cmd" or  user_input=="دستور":
                cmd =input(">\n")
                s=system(cmd)
                print(s)
                
            
                
            bot_response = self.get_chat_response(user_input)
            print("ChatBot:", bot_response)

        # Record the executed code along with user input and bot response
        self.record_code(code_content, user_input, bot_response)

        # List chat history and export to CSV
        self.list_chat()
        self.export_to_csv()


if __name__ == "__main__":
    bot = ChatBot()
    bot.main()
