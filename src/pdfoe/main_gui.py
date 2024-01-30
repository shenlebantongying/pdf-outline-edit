import subprocess
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import idlelib.colorizer as ic
import idlelib.percolator as ip

import traceback
import os.path
import webbrowser

from . import pdf_obj
from .common import *


class CustomTextWidget(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.internal_text_widget = tk.Text(self, wrap="none", width=1, height=1)

        self.internal_text_widget.config(
            tabs=tk.font.Font(font=self.internal_text_widget["font"]).measure("    ")
        )

        self.internal_text_widget.bind("<Control-Key-a>", self.select_all)
        self.internal_text_widget.bind("<Control-Key-A>", self.select_all)

        # Scrollbars
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
        return self.internal_text_widget.get("1.0", tk.END)

    def set_text(self, ss: str):
        self.internal_text_widget.delete("1.0", tk.END)
        self.internal_text_widget.insert("1.0", ss)

    # noinspection PyUnusedLocal
    def select_all(self, event):
        self.internal_text_widget.tag_add(tk.SEL, "1.0", tk.END)
        return "break"


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

        file_label = ttk.Label(file_row_frame, text="Target PDF file path: ")
        btn_file_open = ttk.Button(
            file_row_frame, text="Set path", command=self.callback_openfile
        )
        file_line_entry = ttk.Entry(
            file_row_frame, textvariable=self.fileLine_entry_text
        )

        file_label.pack(side=tk.LEFT)
        file_line_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        btn_file_open.pack(side=tk.LEFT)

        additional_row_label = ttk.Label(additional_row_frame, text="Extra tools: ")
        btn_import_existing_toc = ttk.Button(
            additional_row_frame,
            text="Import existing outlines",
            command=self.callback_import_existing_toc,
        )
        btn_tidy_up = ttk.Button(
            additional_row_frame, text="Tidy up", command=self.callback_tidy_up
        )

        btn_auto_indent = ttk.Button(
            additional_row_frame,
            text="Auto indent by heads",
            command=self.callback_auto_indent_by_heading,
        )

        btn_open_pdf = ttk.Button(
            additional_row_frame,
            text="Open file in PDF viewer",
            command=self.callback_open_pdf_file,
        )

        additional_row_label.pack(side=tk.LEFT)
        btn_import_existing_toc.pack(side=tk.LEFT)
        btn_open_pdf.pack(side=tk.LEFT)
        btn_tidy_up.pack(side=tk.LEFT)
        btn_auto_indent.pack(side=tk.LEFT)

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
        self.offset_spin.set(0)

        # bottom
        btn_accept = ttk.Button(
            bottom_frame,
            text="Write outline to target PDF...",
            command=self.callback_write_outline_now,
        )
        btn_accept.pack(side=tk.RIGHT)

        btn_help = ttk.Button(
            bottom_frame,
            text="Help",
            command=lambda: webbrowser.open(
                "https://github.com/shenlebantongying/pdf-outline-edit"
            ),
        )
        btn_help.pack(side=tk.LEFT)

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
        if path := self.get_current_pdf_file():
            temp_pdf = pdf_obj.MyPDF(path)
            (text, offset) = temp_pdf.get_toc_as_text()
            self.text_the_main_thing.set_text(text)
            self.offset_spin.set(offset)
        else:
            gui_popup_error("PDF file file doesn't exist.")

    def callback_write_outline_now(self):
        if path := self.get_current_pdf_file():
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
        text = self.text_the_main_thing.get_all_text()
        ret_text = []

        for line in text.splitlines():
            # remove right side white space
            line = line.rstrip()

            # skip empty lines
            if line == "":
                continue

            try:
                entry = parse_line(line)
            except Exception as e:
                gui_popup_error(str(e))
                return

            # remove excessive white spaces in title
            entry.title = " ".join(entry.title.split())

            # remove unnecessary ending punctuations
            entry.title = entry.title.rstrip(",.")

            ret_text.append(entry.to_string())

        self.text_the_main_thing.set_text("\n".join(ret_text))

    def callback_open_pdf_file(self):
        filename = self.get_current_pdf_file()
        if filename is None:
            gui_popup_error("PDF file file doesn't exist.")
            return
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def callback_auto_indent_by_heading(self):
        self.callback_tidy_up()

        text = self.text_the_main_thing.get_all_text()
        cur_num = 0

        ret_text = []

        for line in text.splitlines():
            try:
                entry = parse_line(line)
            except Exception as e:
                gui_popup_error(str(e))
                return

            head = entry.title.split(maxsplit=1)[0]
            head_num: int
            try:
                head_num = int(head)
            except ValueError:
                head_num = -1

            if head_num == (cur_num + 1):
                entry.level = 0
                cur_num += 1
            else:
                entry.level = 1

            ret_text.append(entry.to_string())
            self.text_the_main_thing.set_text("\n".join(ret_text))


def main():
    App()
