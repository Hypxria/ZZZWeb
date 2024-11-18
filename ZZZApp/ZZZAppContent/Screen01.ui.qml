

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

    Rectangle {
        id: rectangle2
        x: 540
        y: 80
        width: 200
        height: rectangle2.width
        color: "#762f2f"
    }

    Rectangle {
        id: rectangle3
        x: 434
        y: 378
        width: controller.width
        height: 14
        visible: true
        color: "#2153ed"
        transformOrigin: Item.Left

        Connections {
            target: rectangle3
            onActiveFocusChanged: console.log("clicked")
        }
    }

    Image {
        id: image
        x: 540
        y: 80
        width: 200
        height: 200
        source: controller.songUrl
        fillMode: Image.PreserveAspectFit
    }

    states: [
        State {
            name: "SpotifyMenu"
            when: roundButtonSpotify.checked

            PropertyChanges {
                target: rectangle3
                visible: true
            }

            PropertyChanges {
                target: rectangle2
                x: 523
                y: 68
                width: 235
                height: rectangle2.width
            }

            PropertyChanges {
                target: image
                x: 523
                y: 68
                width: 235
                height: 229
            }
        },
        State {
            name: "ZenlessMenu"
            when: roundButtonZenless.checked

            PropertyChanges {
                target: roundButtonZenless
                checkable: true
            }
        }
    ]
}
