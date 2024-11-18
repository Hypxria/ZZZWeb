

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls
import ZZZApp
import QtQuick.Studio.Components 1.0

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height

    color: Constants.backgroundColor

    Rectangle {
        id: rectangle1
        y: -69
        width: 192
        height: 115
        color: "#ffffff"
        radius: 7
        anchors.horizontalCenter: parent.horizontalCenter
        z: 0

        Row {
            x: 462
            height: 37
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: 35
            anchors.horizontalCenter: parent.horizontalCenter
            layoutDirection: Qt.LeftToRight
            spacing: 32

            RoundButton {
                id: roundButtonSpotify
                width: 36
                height: 36
                text: "+"
                autoExclusive: true
                checkable: false

                Switch {
                    id: spotifyCoverSwitch
                    x: -2
                    y: 0
                    width: 40
                    height: 40
                    opacity: 0
                    autoExclusive: true

                    Connections {
                        target: spotifyCoverSwitch
                        onCheckedChanged: roundButtonSpotify.checked = spotifyCoverSwitch.checked
                    }

                    Connections {
                        target: spotifyCoverSwitch
                        onToggled: zenlessCoverSwitch.checked = false
                    }
                }
            }

            RoundButton {
                id: roundButtonBoth
                width: 36
                height: 36
                text: "+"
                flat: false
                checkable: true
                autoExclusive: true

                Connections {
                    target: roundButtonBoth
                    onToggled: spotifyCoverSwitch.checked = false
                }

                Connections {
                    target: roundButtonBoth
                    onToggled: zenlessCoverSwitch.checked = false
                }
            }

            RoundButton {
                id: roundButtonZenless
                width: 36
                height: 36
                text: "+"
                autoExclusive: true
                checkable: false

                Switch {
                    id: zenlessCoverSwitch
                    x: 0
                    y: 0
                    width: 36
                    height: 36
                    opacity: 0
                    visible: true
                    autoExclusive: true
                    checkable: true

                    Connections {
                        target: zenlessCoverSwitch
                        onCheckedChanged: roundButtonZenless.checked = zenlessCoverSwitch.checked
                    }

                    Connections {
                        target: zenlessCoverSwitch
                        onToggled: spotifyCoverSwitch.checked = false
                    }
                }
            }
        }

        GroupItem {
            x: 8
            y: 72
        }
    }

    Text {
        id: _text
        x: 210
        y: 220
        visible: roundButtonSpotify.checked
        text: qsTr("Text")
        font.pixelSize: 12
    }

    Rectangle {
        id: rectangle2
        x: 529
        y: 182
        width: 303
        height: 200
        color: "#762f2f"

        Slider {
            id: slider
            x: 52
            y: 80
            value: 0.2
        }
    }

    Rectangle {
        id: rectangle3
        x: controller.x
        y: controller.y
        width: controller.width
        height: 14
        color: "#2153ed"
    }

    Text {
        id: _text1
        x: 299
        y: 111
        visible: roundButtonZenless.checked
        text: "test"
        font.pixelSize: 12
    }

    Text {
        id: _text2
        x: 637
        y: 192
        color: "#ffffff"
        text: "backend.data"
        font.pixelSize: 12
    }

    ProgressBar {
        id: progressBar
        x: 542
        y: 325
        width: 275
        height: 6
        value: 0.5
    }

    states: [
        State {
            name: "SpotifyMenu"
            when: roundButtonSpotify.checked

            PropertyChanges {
                target: _text
                x: 210
                y: 61
                width: 356
                height: 175
                visible: roundButtonSpotify.checked
                text: qsTr("Spotify")
                font.pixelSize: 59
            }

            PropertyChanges {
                target: _text1
                x: 671
                y: 207
            }
        },
        State {
            name: "ZenlessMenu"
            when: roundButtonZenless.checked

            PropertyChanges {
                target: roundButtonZenless
                checkable: true
            }

            PropertyChanges {
                target: _text1
                visible: roundButtonZenless.checked
                text: qsTr("Zenless")
                font.pixelSize: 59
            }
        }
    ]
}
