import sys
import re
from pathlib import Path

from PySide6.QtGui import (
    QGuiApplication,
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QTextDocument,
)
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickTextDocument
from PySide6.QtCore import QObject, Slot, Signal, Property, QUrl

from . import pdf_obj

MAIN_TEXT = "main_text"
PATH_TEXT = "path_text"
OFFSET = "offset"


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        QSyntaxHighlighter.__init__(self, parent)
        self.the_regex = re.compile(
            r"^(?P<indents>[\s]*)(?P<title>[\S\s]+?)\s+(?P<page_num>\d+)$"
        )
        self.title_format = QTextCharFormat()
        self.title_format.setForeground(QColor("#880089"))
        self.color_format = QTextCharFormat()
        self.color_format.setForeground(QColor("#308A00"))

    def highlightBlock(self, text):

        self.the_regex.findall(text)

        for i in self.the_regex.finditer(text):
            self.setFormat(i.span(2)[0], i.span(2)[1] - i.span(2)[0], self.title_format)
            self.setFormat(i.span(3)[0], i.span(3)[1] - i.span(3)[0], self.color_format)


class Holy(QObject):
    def __init__(self):
        super().__init__()

    def set_qmlapp(self, o):
        self.qmlapp = o

    @Slot(QObject)
    def set_text_edit_obj(self, o: QQuickTextDocument):
        doc: QTextDocument = o.textDocument()
        hl = Highlighter(self)
        hl.setDocument(doc)
        # NOTE: setting QTextOptions via QTextDocument does not work as of Qt6.6

    def get_main_text(self) -> str:
        return self.qmlapp.property(MAIN_TEXT)

    def set_main_text(self, s: str):
        self.qmlapp.setProperty(MAIN_TEXT, s)

    def get_path(self) -> str:
        return self.qmlapp.property(PATH_TEXT)

    def get_offset(self) -> int:
        return self.qmlapp.property(OFFSET)

    @Slot()
    def process(self):
        path = QUrl(self.get_path()).path()
        temp_pdf = pdf_obj.MyPDF(path)
        print(self.get_main_text())
        temp_pdf.set_toc_according_to_text(
            self.get_main_text(),
            self.get_offset(),
        )


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    holy = Holy()
    engine.rootContext().setContextProperty("holy", holy)
    engine.load(Path(__file__).resolve().parent / "main.qml")

    qml_app: QObject = engine.rootObjects()[0]

    holy.set_qmlapp(qml_app)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
