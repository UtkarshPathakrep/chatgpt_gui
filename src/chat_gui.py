import tkinter as tk
from tkinter import scrolledtext
import mysql.connector
from datetime import datetime
from openai import OpenAI
from src.config import OPENAI_API_KEY, MYSQL_CONFIG
from src.mysql_connection import init_database


def setup_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT GUI")
        self.root.geometry("600x500")

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, state='disabled')
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_field = tk.Entry(root, width=50)
        self.input_field.pack(padx=10, pady=5, side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=5, pady=5, side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Clear", command=self.clear_chat)
        self.clear_button.pack(padx=5, pady=5, side=tk.LEFT)

        init_database()
        self.client = setup_openai_client()
        self.load_conversation()

    def display_message(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def load_conversation(self):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT user_input, model_response FROM conversations ORDER BY timestamp')
            for user_input, model_response in cursor.fetchall():
                self.display_message("You", user_input)
                if model_response:
                    self.display_message("GPT-4o-mini", model_response)
        except mysql.connector.Error as e:
            self.display_message("Error", f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    def save_conversation(self, user_input, model_response):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor()
            timestamp = datetime.now()
            cursor.execute('INSERT INTO conversations (user_input, model_response, timestamp) VALUES (%s, %s, %s)',
                          (user_input, model_response, timestamp))
            conn.commit()
        except mysql.connector.Error as e:
            self.display_message("Error", f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.display_message("You", user_input)
        self.input_field.delete(0, tk.END)

        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT user_input, model_response FROM conversations ORDER BY timestamp DESC LIMIT 5')
            history = cursor.fetchall()[::-1]
        except mysql.connector.Error as e:
            self.display_message("Error", f"Database error: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        messages = []
        for user_msg, model_msg in history:
            messages.append({"role": "user", "content": user_msg})
            if model_msg:
                messages.append({"role": "assistant", "content": model_msg})
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            model_response = response.choices[0].message.content.strip()

            self.display_message("GPT-4o-mini", model_response)
            self.save_conversation(user_input, model_response)

        except Exception as e:
            self.display_message("Error", f"Failed to get response: {e}")

    def clear_chat(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations')
            conn.commit()
        except mysql.connector.Error as e:
            self.display_message("Error", f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

