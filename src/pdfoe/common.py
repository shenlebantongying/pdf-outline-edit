import tkinter.messagebox as messagebox


def gui_popup_error(msg: str, title: str = "whoops!"):
    messagebox.showerror(title=title, message=msg)
