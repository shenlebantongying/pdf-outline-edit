# Mini PDF Outline Editor

```
pipx run pdf-outline-edit
```

A GUI program to import, edit and modify PDF outlines/Table-of-Content through a simple textual format.

The textual format is almost the same as printed books' ToC which has been "rediscovered" multiple times.

1. Indent level -> Nesting level
2. Number at the end -> Page number
3. Text in between -> Title

You can copy and paste existing outline from PDF books and tidy it up a bit to fuse it into the PDF file in 3 easy steps:

1. Set a target PDF file
2. Write the outline
3. Press "Write to PDF" button

<img src="demo.svg" alt="demo"/>

Extra features

Automatic tidy up button. It does the following:

1. Guess and adjust indent levels
2. Remove excessive spaces

Extra Options

* Offset: Starting page of the page numbers. The pages before it will be roman numerals and the offset page's page label will be 1.

# Alternatives

* [HandyOutliner](https://handyoutlinerfo.sourceforge.net/) Almost identical program but written in .NET & iText and uses XML
* [pdf.tocgen](https://github.com/Krasjet/pdf.tocgen) Over-engineered by following the disgusting "unix philo-dogshit-sophy".

# DevOops

```sh
# Install in virtualenv
python3 -m pip install -e .

# Run in dev environment
./src/run-gui.py
```

# License

AGPL-3.0-or-later
