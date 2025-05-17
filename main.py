

import tkinter
from src.chat_gui import ChatGUI
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    root = tkinter.Tk()
    app = ChatGUI(root)
    root.mainloop()