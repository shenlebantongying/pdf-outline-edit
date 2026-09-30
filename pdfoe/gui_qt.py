import re
import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import (
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QApplication,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument):
        super().__init__(parent)
        self.the_regex = re.compile(
            r"^(?P<indents>[\s]*)(?P<title>[\S\s]+?)\s+(?P<page_num>\d+)$"
        )

        self.indent_format = QTextCharFormat()
        self.indent_format.setForeground(QColor("#880089"))
        self.indent_format.setBackground(QColor("#880089"))

        self.title_format = QTextCharFormat()
        self.title_format.setForeground(QColor("#880089"))
        self.color_format = QTextCharFormat()
        self.color_format.setForeground(QColor("#308A00"))

    def highlightBlock(self, text):
        self.the_regex.findall(text)
        for i in self.the_regex.finditer(text):
            self.setFormat(i.span(1)[0], i.span(1)[1] - i.span(1)[0], self.indent_format)
            self.setFormat(i.span(2)[0], i.span(2)[1] - i.span(2)[0], self.title_format)
            self.setFormat(i.span(3)[0], i.span(3)[1] - i.span(3)[0], self.color_format)



class MyApp(QWidget):
    def __init__(self, /):
        super().__init__()
        self.resize(800,600)
        self.layout:QVBoxLayout = QVBoxLayout(self)
        self.btn = QPushButton("say hi")
        self.btn.clicked.connect(self.print_hi)
        self.layout.addWidget(self.btn)


        self.textedit = QPlainTextEdit(self)

        self.hl = Highlighter(self.textedit.document())
        self.layout.addWidget(self.textedit)

    @Slot()
    def print_hi(self):
        print("hi")



def main():
    app = QApplication([])
    widget = MyApp()
    widget.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

