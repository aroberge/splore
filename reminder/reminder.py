import tkinter as tk
import win10toast


class App:
    def __init__(self, parent):
        self.parent = parent
        parent.title("Periodic reminder")
        parent.geometry("280x120")
        parent.grid_columnconfigure((0, 1), weight=1)

        self.message = tk.StringVar()
        self.message.set("Reminder message here")
        tk.Entry(self.parent, textvariable=self.message).grid(
            row=1, column=1, sticky="ew"
        )
        tk.Label(self.parent, text="Message").grid(row=1, column=0)

        tk.Label(self.parent, text="Repeat interval").grid(
            row=2, column=0, columnspan=2
        )

        self.hours = tk.IntVar()
        self.hours.set(0)
        tk.Entry(self.parent, textvariable=self.hours).grid(
            row=3, column=1, sticky="ew"
        )
        tk.Label(self.parent, text="Hours").grid(row=3, column=0)

        self.minutes = tk.IntVar()
        self.minutes.set(60)
        tk.Entry(self.parent, textvariable=self.minutes).grid(
            row=4, column=1, sticky="ew"
        )
        tk.Label(self.parent, text="Minutes").grid(row=4, column=0)

        self.start_job_btn = tk.Button(parent, text="Start job", command=self.start_job)
        self.start_job_btn.grid(row=5, column=0)

        self.close_btn = tk.Button(parent, text="Close", command=parent.quit)
        self.close_btn.grid(row=5, column=1)

    def start_job(self):
        toaster = win10toast.ToastNotifier()
        toaster.show_toast(
            "Friendly reminder",
            self.message.get(),
            duration=10,
            icon_path="",
            threaded=True,
        )
        self.parent.after(
            (3600 * self.hours.get() + 60 * self.minutes.get()) * 1000, self.start_job
        )


parent = tk.Tk()
app = App(parent)
parent.mainloop()
