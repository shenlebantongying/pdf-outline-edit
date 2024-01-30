import fitz
from .common import *


class MyPDF:
    def __init__(self, pdf_file_path: str):
        self.path: str = pdf_file_path

    def get_toc_as_text(self) -> tuple[str, int]:
        with fitz.open(self.path) as doc:

            offset = 0
            for label in doc.get_page_labels():
                if label['style'] == 'D' and label['startpage'] != 0:
                    offset = label['startpage']

            toc = fitz.utils.get_toc(doc, simple=True)
            ret: list[str] = []
            for i in toc:
                level = int(i[0]) - 1
                ret.append((level if level > 0 else 0) * "\t")
                ret.append(i[1])
                ret.append(" ")
                ret.append(str(i[2] - offset))
                ret.append("\n")
            return "".join(ret), offset - 1

    def set_toc_according_to_text(
            self,
            text: str,
            offset: int,
    ):
        offset = offset + 1
        with fitz.open(self.path) as doc:
            fitz.utils.set_page_labels(
                doc,
                [
                    {"startpage": 0, "prefix": "", "style": "r", "firstpagenum": 1},
                    {
                        "startpage": offset,
                        "prefix": "",
                        "style": "D",
                        "firstpagenum": 1,
                    },
                ],
            )

            toc = []

            for line in text.splitlines():
                # calculate tab numbers and plus one
                line.rstrip()

                # skip empty lines
                if line == "":
                    continue

                try:
                    entry = parse_line(line)
                except Exception as e:
                    gui_popup_error(str(e))
                    return

                toc.append(
                    [
                        entry.level + 1,
                        entry.title,
                        entry.page_num + offset,
                    ]
                )

            fitz.utils.set_toc(doc, toc, collapse=0)
            doc.saveIncr()
