'''Simple grid - playing with geometry'''

import tkinter as tk

root = tk.Tk()
root.title("Credentials entry")

name_label = tk.Label(root, text="username")
name_input = tk.Entry(root)

password_label = tk.Label(root, text="password")
password_input = tk.Entry(root, show="•")

name_label.grid(row=0, column=0)
name_input.grid(row=0, column=1)

password_label.grid(row=1, column=0)
password_input.grid(row=1, column=1)

root.mainloop()
