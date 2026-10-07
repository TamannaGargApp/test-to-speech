import tkinter as tk
import requests


def convert():

    text = entry.get()

    requests.post("http://localhost:8000/speech", json={"text": text})


root = tk.Tk()

entry = tk.Entry(root)

entry.pack()

button = tk.Button(root, text="Convert", command=convert)

button.pack()

root.mainloop()
