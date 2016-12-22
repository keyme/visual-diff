#!/usr/bin/python3
import tkinter as tk

class Example(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.l1 = tk.Label(self, text="Hover over me")
        self.l2 = tk.Label(self, text="", width=40)
        self.l1.pack(side="top")
        self.l2.pack(side="top", fill="x")

        self.l1.bind("<Enter>", self.on_enter)
        self.l1.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        #print("{} ({}): {}".format(event, type(event), dir(event)))
        print("({}, {})".format(event.x, event.y))
        self.l2.configure(text="Hello world")

    def on_leave(self, event):
        #print("{} ({}): {}".format(event, type(event), dir(event)))
        print("({}, {})".format(event.x, event.y))
        self.l2.configure(text="")

def on_motion(event):
    print("Motion: ({}, {})".format(event.x, event.y))

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(side="top", fill="both", expand="true")
    root.bind("<Motion>", on_motion)
    root.mainloop()
