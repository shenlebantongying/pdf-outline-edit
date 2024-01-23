from dataclasses import dataclass
import tkinter.messagebox as messagebox
import re


@dataclass
class LineEntry:
    level: int
    title: str
    page_num: int

    def to_string(self):
        tab = "\t"  # python3.11's f-string cannot contain backslash. 😅
        return f"{tab* self.level}{self.title} {self.page_num}"


the_regex = re.compile(r"^\t*(?P<title>[\S\s]+)\s+(?P<page_num>\d+)$")

regex_title_name = "title"
regex_page_num_name = "page_num"


def parse_line(line: str) -> LineEntry:
    regex_result = the_regex.match(line)

    if regex_result is None:
        raise Exception("This line has problems ->\n" + line)

    regex_title = regex_result.group(regex_title_name)
    regex_offset = int(regex_result.group(regex_page_num_name))

    if regex_title is None or regex_offset is None:
        raise Exception("This line has problems ->\n" + line)

    return LineEntry(count_starting_tabs(line), regex_title, regex_offset)


def count_starting_tabs(s: str):
    ret = 0
    for c in s:
        if c == "\t":
            ret += 1
        else:
            break
    return ret


def gui_popup_error(msg: str, title: str = "whoops!"):
    messagebox.showerror(title=title, message=msg)
