import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import idlelib.colorizer as ic
import idlelib.percolator as ip

import re
import traceback
import os.path

from . import pdf_obj
from .common import *


class CustomTextWidget(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.internal_text_widget = tk.Text(self, wrap="none", width=1, height=1)

        self.internal_text_widget.config(
            tabs=tk.font.Font(font=self.internal_text_widget["font"]).measure("    ")
        )

        ys = ttk.Scrollbar(
            self, orient="vertical", command=self.internal_text_widget.yview
        )
        xs = ttk.Scrollbar(
            self, orient="horizontal", command=self.internal_text_widget.xview
        )
        self.internal_text_widget["yscrollcommand"] = ys.set
        self.internal_text_widget["xscrollcommand"] = xs.set

        xs.grid(column=0, row=1, sticky="we")
        ys.grid(column=1, row=0, sticky="ns")
        self.internal_text_widget.grid(column=0, row=0, sticky="nesw")
        self.grid_columnconfigure(0, weight=1, uniform="1")
        self.grid_rowconfigure(0, weight=1, uniform="1")

        # tk.Text colorizer from idlelib
        cdg = ic.ColorDelegator()
        cdg.prog = re.compile(
            r"^(?P<indents>\t*)(?P<title>[\S\s]+?)\s+(?P<page_num>\d+)$",
            re.MULTILINE,
        )

        cdg.tagdefs["indents"] = {"foreground": "#FFFFFF", "background": "#E0FFE7"}
        cdg.tagdefs["title"] = {"foreground": "#880089", "background": "#FFFFFF"}
        cdg.tagdefs["page_num"] = {"foreground": "#308A00", "background": "#FFFFFF"}

        ip.Percolator(self.internal_text_widget).insertfilter(cdg)

    def get_all_text(self):
        return self.internal_text_widget.get("1.0", "end")

    def set_text(self, ss: str):
        self.internal_text_widget.delete("1.0", "end")
        self.internal_text_widget.insert("1.0", ss)


class App:
    def __init__(self):
        # GUI
        self.root = tk.Tk()
        self.root.title("Mini PDF outline Editor")

        # 3 parts
        top_frame = ttk.Frame(self.root)
        text_frame = ttk.Frame(self.root)
        bottom_frame = ttk.Frame(self.root)

        top_frame.grid(row=0, column=0, sticky="nesw")
        text_frame.grid(row=1, column=0, sticky="nesw")
        text_frame.grid(row=1, column=0, sticky="nesw")
        bottom_frame.grid(row=2, column=0, stick="nesw")
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)

        self.root.grid_columnconfigure(0, weight=1, minsize=400)

        # constructing top

        file_row_frame = ttk.Frame(top_frame)
        additional_row_frame = ttk.Frame(top_frame)

        self.fileLine_entry_text = tk.StringVar()

        file_label = ttk.Label(file_row_frame, text="Target PDF file")
        btn_file_open = ttk.Button(
            file_row_frame, text="Open file", command=self.callback_openfile
        )
        file_line_entry = ttk.Entry(
            file_row_frame, textvariable=self.fileLine_entry_text
        )

        file_label.pack(side=tk.LEFT)
        file_line_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        btn_file_open.pack(side=tk.LEFT)

        additional_row_label = ttk.Label(additional_row_frame, text="Extra tools:")
        btn_import_existing_toc = ttk.Button(
            additional_row_frame,
            text="Import existing TOC",
            command=self.callback_import_existing_toc,
        )
        btn_clean = ttk.Button(
            additional_row_frame, text="Tidy up TOC", command=self.callback_tidy_up
        )

        additional_row_label.pack(side=tk.LEFT)
        btn_clean.pack(side=tk.LEFT)

        btn_import_existing_toc.pack(side=tk.LEFT)

        file_row_frame.pack(side=tk.TOP, fill=tk.BOTH)
        additional_row_frame.pack(side=tk.TOP, fill=tk.BOTH)

        # text input area
        self.text_the_main_thing = CustomTextWidget(text_frame)
        self.text_the_main_thing.grid(column=0, row=0, sticky="nesw")
        text_frame.grid_columnconfigure(0, weight=1, uniform="1")
        text_frame.grid_rowconfigure(0, weight=1, uniform="1")

        advanced_options_frame = ttk.Frame(text_frame)
        advanced_options_frame.grid(column=1, row=0, sticky="n")
        text_frame.grid_columnconfigure(1, weight=0)

        offset_line_frame = ttk.Frame(advanced_options_frame)
        offset_line_frame.pack(side=tk.TOP)

        offset_label = ttk.Label(offset_line_frame, text="Offset")
        offset_label.pack(side=tk.LEFT)

        self.offset_spin = ttk.Spinbox(offset_line_frame, from_=0, to=99999, width=4)
        self.offset_spin.pack(side=tk.LEFT)

        # bottom
        btn_accept = ttk.Button(
            bottom_frame,
            text="Write outline to target PDF...",
            command=self.callback_write_outline_now,
        )
        btn_accept.pack(side=tk.RIGHT)

        btn_help = ttk.Button(bottom_frame, text="Help")
        btn_help.pack(side=tk.LEFT)

        # menubar
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="About",
        )
        menubar.add_cascade(label="Help", menu=filemenu)

        self.root.config(menu=menubar)

        self.root.geometry("800x500")
        self.root.mainloop()

    def get_current_pdf_file(self):
        p = self.fileLine_entry_text.get()
        return p if os.path.exists(p) else None

    def callback_openfile(self):
        r = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if r != "":
            self.fileLine_entry_text.set(r)

    def callback_import_existing_toc(self):
        if path := self.get_current_pdf_file() is not None:
            temp_pdf = pdf_obj.MyPDF(path)
            self.text_the_main_thing.set_text(temp_pdf.get_toc_as_text())
        else:
            gui_popup_error("PDF file file doesn't exist.")

    def callback_write_outline_now(self):
        if path := self.get_current_pdf_file() is not None:
            temp_pdf = pdf_obj.MyPDF(path)
            try:
                temp_pdf.set_toc_according_to_text(
                    self.text_the_main_thing.get_all_text(),
                    int(self.offset_spin.get()),
                )
            except Exception as ex:
                m = "Error!\n"
                m += str(ex)
                m += "\n"
                m += str(traceback.format_exc())
                gui_popup_error(m)
        else:
            gui_popup_error("PDF file doesn't exist.")

    def callback_tidy_up(self):
        pass


def main():
    App()
