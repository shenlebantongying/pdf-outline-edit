import importlib.util


def main():
    PySide6_spec = importlib.util.find_spec("PySide6")
    if PySide6_spec is not None:
        from . import gui_pyside_qml

        gui_pyside_qml.main()
    else:
        from . import gui_tkinter

        gui_tkinter.main()
