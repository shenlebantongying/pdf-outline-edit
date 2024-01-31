import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Dialogs

ApplicationWindow {
    property alias main_text: text_main.text
    property alias path_text: path_text.text
    property alias offset: spin_offset.value

    Component.onCompleted: {
        holy.set_text_edit_obj(text_main.textDocument);
    }
    width: 800
    height: 600
    visible: true
    title: qsTr("PDF outline edit")

    ColumnLayout {
        anchors.margins: 3
        anchors.fill: parent

        RowLayout {
            id: layout

            Layout.fillWidth: true

            Label {
                text: "Target PDF file path: "
            }

            TextField {
                id: path_text

                Layout.fillWidth: true
                verticalAlignment: TextInput.AlignVCenter
            }

            Button {
                text: "Set path"
                onClicked: fileDialog.open()
            }

            FileDialog {
                id: fileDialog

                onAccepted: {
                    path_text.text = selectedFile;
                }
            }

        }

        RowLayout {
            Label {
                text: "Extra tools: "
            }

            Button {
                text: "Import outlines from PDF"
            }

            Button {
                text: "Open in PDF viewer"
            }

            Button {
                text: "Tidy up"
            }

            Button {
                text: "Auto indent by heads"
            }

        }

        Frame {
            Layout.fillHeight: true
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent

                ScrollView {
                        Layout.fillHeight: true
                        Layout.fillWidth: true

                    TextArea {
                        id: text_main
                        tabStopDistance:20

                        background: Rectangle {
                            border.color: text_main.activeFocus ? "green" : "gray"
                        }

                    }

                }

                GridLayout {
                    Layout.alignment: Qt.AlignTop
                    columns: 2

                    Label {
                        text: "Offset"
                    }

                    SpinBox {
                        id: spin_offset

                        value: 0
                        editable: true
                    }

                }

            }

        }

        RowLayout {
            Button {
                text: "Help"
                onClicked: text_main.verticalAlignment = TextEdit.AlignRight
            }

            Rectangle {
                Layout.fillWidth: true
            }

            Button {
                text: "Write outline to target PDF..."
                onClicked: holy.process()
            }

        }

    }

}
