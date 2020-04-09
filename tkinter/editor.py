import os
import tkinter as tk
from tkinter import filedialog

import keyword
import tokenize
from io import StringIO


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """
    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]


class TextEditor:
    def __init__(self, root, title="Title"):
        self.text_to_write = ""
        root.title(title)
        root.geometry("600x550")
        frame = tk.Frame(root, width=600, height=550)
        y_scrollbar = tk.Scrollbar(frame)
        self.text_area = tk.Text(
            frame,
            wrap=tk.NONE,
            width=600,
            height=550,
            yscrollcommand=y_scrollbar.set,
            padx=10,
            pady=10,
            font="Helvetica 11",
        )
        y_scrollbar.config(command=self.text_area.yview)
        y_scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)
        self.text_area.tag_config("blue", foreground="blue")
        self.text_area.tag_config(
#            "bold", font="Helvetica 11 bold", foreground="dark violet"
            "bold", font="Helvetica 11 bold", foreground="lime green"
        )

        frame.pack()
        self.make_menu(root)

    def make_menu(self, root):
        """Makes the main menu"""
        menu = tk.Menu(root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_app)
        menu.add_cascade(label="File", menu=file_menu)
        root.config(menu=menu)

    def open_file(self, event=None):
        """Opens a file by looking first from the current directory."""
        txt_file = filedialog.askopenfilename(parent=root, initialdir=os.getcwd())
        if txt_file:
            self.text_area.delete(1.0, tk.END)
            with open(txt_file) as new_file:
                content = new_file.read()
                self.text_area.insert(1.0, content)
                root.update_idletasks()

        tokens = tokenize.generate_tokens(StringIO(content).readline)
        for tok in tokens:
            token = Token(tok)
            if token.string in keyword.kwlist:
                begin_index = "{0}.{1}".format(token.start_line, token.start_col)
                end_index = "{0}.{1}".format(token.end_line, token.end_col)
                self.text_area.tag_add("bold", begin_index, end_index)

    def save_file(self, event=None):
        """Saves the file currently in the Texteditor"""
        file = filedialog.asksaveasfile(mode="w")
        if file is not None:
            data = self.text_area.get("1.0", tk.END)
            file.write(data)
            file.close()

    # Quits the TkInter app when called
    @staticmethod
    def quit_app(event=None):
        """Simply quits the app"""
        root.quit()


root = tk.Tk()
text_editor = TextEditor(root, title="Root")
top = tk.Toplevel()
text_editor2 = TextEditor(top, title="Top")

root.mainloop()
