

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
        id: baseMenu
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
    Slider {
        id: customSlider
        x: 194
        y: 214
        width: 200
        height: 20
        value: 0.5
        anchors.horizontalCenterOffset: 429
        // Initial value (0.0 to 1.0)

        // Custom styling
        background: Rectangle {
            x: customSlider.leftPadding
            y: customSlider.topPadding + customSlider.availableHeight / 2 - height / 2
            width: customSlider.availableWidth
            height: 4 // Height of the slider track
            radius: 2
            color: "#e0e0e0" // Empty/background color

            // This is the filled portion
            Rectangle {
                width: customSlider.visualPosition * parent.width
                height: parent.height
                color: "#1db954" // Fill color
                radius: 2
            }
        }

        // Custom handle (the part you drag)
        handle: Rectangle {
            x: customSlider.leftPadding + customSlider.visualPosition
               * (customSlider.availableWidth - width)
            y: customSlider.topPadding + customSlider.availableHeight / 2 - height / 2
            width: 16
            height: 16
            opacity: 1
            radius: 8
            color: customSlider.pressed ? "#f0f0f0" : "#ffffff"
            border.color: "#1db954"
            border.width: 0
        }
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
                y: 56
                width: 235
                height: rectangle2.width
            }

            PropertyChanges {
                target: image
                x: 772
                y: 56
                width: 235
                height: 229
            }

            PropertyChanges {

                target: customSlider
                x: (parent.width - width) / 2  // This centers it horizontally
                y: 311
                width: 1103
                height: 20
                value: 0.5
                anchors.horizontalCenterOffset: 0
                transformOrigin: Item.Center
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
