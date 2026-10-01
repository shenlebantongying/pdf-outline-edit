import os
import re
import subprocess
import sys

from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import (
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
    QFont,
    QFontMetricsF,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from pdfoe import pdf_obj

from .common import MyException, parse_line


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument):
        super().__init__(parent)
        self.the_regex = re.compile(
            r"^(?P<indents>\s*)(?P<title>[\S\s]+?)\s+(?P<page_num>\d+)$"
        )

        self.indent_fmt = QTextCharFormat()
        self.indent_fmt.setBackground(QColor("#E0FFE7"))

        self.title_fmt = QTextCharFormat()
        self.title_fmt.setForeground(QColor("#880089"))

        self.color_fmt = QTextCharFormat()
        self.color_fmt.setForeground(QColor("#308A00"))

    def highlightBlock(self, text):
        self.the_regex.findall(text)
        for i in self.the_regex.finditer(text):
            self.setFormat(i.span(1)[0], i.span(1)[1] - i.span(1)[0], self.indent_fmt)
            self.setFormat(i.span(2)[0], i.span(2)[1] - i.span(2)[0], self.title_fmt)
            self.setFormat(i.span(3)[0], i.span(3)[1] - i.span(3)[0], self.color_fmt)


class MyApp(QMainWindow):
    def __init__(self, /):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("Mini PDF outline editor")
        self.setWindowIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        )

        # path line
        self.pathline: QLineEdit = QLineEdit(self)
        self.btn_choose_file: QPushButton = QPushButton("Choose File", self)
        _ = self.btn_choose_file.clicked.connect(self.choose_file)

        # settings
        self.offset_label: QLabel = QLabel("First page offset:", self)
        self.offset_box: QSpinBox = QSpinBox()

        # toolbox
        self.tool_import_toc = QPushButton("Import existing outline", self)
        self.tool_import_toc.clicked.connect(self.callback_import_existing_toc)

        self.tool_open_reader = QPushButton("Open file in PDF viewer", self)
        self.tool_open_reader.clicked.connect(self.callback_open_pdf_file)

        self.tool_tidy_up = QPushButton("Tidy up", self)
        self.tool_auto_indent = QPushButton("Auto indent", self)

        # main part
        self.textedit: QPlainTextEdit = QPlainTextEdit(self)
        self.textedit.setTabStopDistance(
            QFontMetricsF(self.textedit.font()).horizontalAdvance(" ") * 8
        )
        self._: Highlighter = Highlighter(self.textedit.document())

        # process btn
        self.btn_process: QPushButton = QPushButton("Process")
        _ = self.btn_process.clicked.connect(self.process)

        # layout init
        self.main_layout: QVBoxLayout = QVBoxLayout(self)
        self.path_bar: QHBoxLayout = QHBoxLayout()
        self.tool_bar: QHBoxLayout = QHBoxLayout()
        self.setting_bar: QHBoxLayout = QHBoxLayout()
        self.setup_layout()

    def setup_layout(self) -> None:
        # assembling widgets
        self.setCentralWidget(QWidget())

        self.path_bar.addWidget(self.btn_choose_file)
        self.path_bar.addWidget(self.pathline)

        self.tool_bar.addWidget(self.tool_import_toc)
        self.tool_bar.addWidget(self.tool_open_reader)
        self.tool_bar.addWidget(self.tool_tidy_up)
        self.tool_bar.addWidget(self.tool_auto_indent)

        self.setting_bar.addWidget(self.offset_label)
        self.setting_bar.addWidget(self.offset_box)
        self.setting_bar.addStretch()

        self.main_layout.addLayout(self.path_bar)
        self.main_layout.addLayout(self.tool_bar)
        self.main_layout.addLayout(self.setting_bar)
        self.main_layout.addWidget(self.textedit)
        self.main_layout.addWidget(self.btn_process)

        self.centralWidget().setLayout(self.main_layout)

    def show_warning(self, msg: str):
        QMessageBox.warning(self, "warning", msg)

    @Slot()
    def choose_file(self):
        (filename, _) = QFileDialog.getOpenFileName(filter="*.pdf")
        self.pathline.setText(filename)

    @Slot()
    def get_main_text(self) -> str:
        return self.textedit.toPlainText()

    def get_current_pdf_file(self) -> str | None:
        p = self.pathline.text()
        return p if os.path.exists(p) else None

    @Slot()
    def callback_import_existing_toc(self):
        if path := self.get_current_pdf_file():
            temp_pdf = pdf_obj.MyPDF(path)
            (text, offset) = temp_pdf.get_toc_as_text()
            self.textedit.setPlainText(text)
            self.offset_box.setValue(offset)
        else:
            self.show_warning("PDF file file doesn't exist.")

    @Slot()
    def callback_open_pdf_file(self):
        filename = self.get_current_pdf_file()
        if filename is None:
            self.show_warning("PDF file file doesn't exist.")
            return
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    @Slot()
    def callback_tidy_up(self):
        text = self.get_main_text()
        ret_text = []

        for line in text.splitlines():
            # remove right side white space
            line = line.rstrip()

            # skip empty lines
            if line == "":
                continue

            try:
                entry = parse_line(line)
            except MyException as e:
                self.show_warning(str(e))
                return

            # remove excessive white spaces in title
            entry.title = " ".join(entry.title.split())

            # remove unnecessary ending punctuations
            entry.title = entry.title.rstrip(",.")

            ret_text.append(entry.to_string())

        self.textedit.setPlainText("\n".join(ret_text))

    @Slot()
    def callback_auto_indent_by_heading(self):
        self.callback_tidy_up()

        text = self.get_main_text()
        cur_num = 0

        ret_text = []

        for line in text.splitlines():
            try:
                entry = parse_line(line)
            except MyException as e:
                self.show_warning(str(e))
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
            self.textedit.setPlainText("\n".join(ret_text))

    @Slot()
    def process(self):

        if path_str := self.get_current_pdf_file():
            path = QUrl(path_str).path()

            temp_pdf = pdf_obj.MyPDF(path)
            print(self.get_main_text())
            temp_pdf.set_toc_according_to_text(
                self.get_main_text(),
                self.offset_box.value(),
            )
        else:
            self.show_warning("No path found.")


def main():
    app = QApplication([])
    widget = MyApp()
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
