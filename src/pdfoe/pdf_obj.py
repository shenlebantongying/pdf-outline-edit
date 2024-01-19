import fitz
import re


the_regex = re.compile(r"^\t*(?P<title>[\S\s]+)\s+(?P<page_num>\d+)$")

regex_title_name = "title"
regex_page_num_name = "page_num"


class MyPDF:
    def __init__(self, pdf_file_path):
        self.path = pdf_file_path

    def get_toc_as_text(self) -> str:
        with fitz.open(self.path) as doc:
            toc = fitz.utils.get_toc(doc, simple=True)
            ret: list[str] = []
            for i in toc:
                level = int(i[0]) - 1
                ret.append((level if level > 0 else 0) * "\t")
                ret.append(i[1])
                ret.append(" ")
                ret.append(str(i[2]))
                ret.append("\n")
            return "".join(ret)

    def set_toc_according_to_text(
        self,
        text: str,
        offset: int,
    ):
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

                # get starting tabs
                level = 1
                for c in line:
                    if c == "\t":
                        level += 1
                    else:
                        break

                regex_result = the_regex.match(line)
                # TODO: handle error here

                toc.append(
                    [
                        level,
                        regex_result.group(regex_title_name),
                        int(regex_result.group(regex_page_num_name)) + offset,
                    ]
                )

            fitz.utils.set_toc(doc, toc, collapse=0)
