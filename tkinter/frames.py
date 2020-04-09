# adapted from https://stackoverflow.com/a/6132876/558799

import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.master.title("Grid Manager")

        for r in range(6):
            self.master.rowconfigure(r, weight=1)
        for c in range(5):
            if c in [1, 4]:
                self.master.columnconfigure(c, weight=1)
            tk.Button(master, text="Button {0}".format(c)).grid(
                row=6, column=c, sticky="w"
            )

        Frame1 = tk.Frame(master, bg="red")
        Frame1.grid(row=0, column=0, rowspan=3, columnspan=2, sticky="news")
        Frame2 = tk.Frame(master, bg="blue")
        Frame2.grid(row=3, column=0, rowspan=3, columnspan=2, sticky="news")
        Frame3 = tk.Frame(master, bg="green")
        Frame3.grid(row=0, column=2, rowspan=6, columnspan=3, sticky="news")


root = tk.Tk()
root.geometry("400x200+200+200")
app = Application(master=root)
app.mainloop()
