

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import ZZZApp
import QtQuick.Studio.Components 1.0
import QtQuick.Studio.DesignEffects
import QtQuick.Studio.Application
import QtQuick.Layouts
import QtQuick.Effects
import QtQuick.Controls.Basic

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height

    color: Constants.backgroundColor

    GroupItem {
        id: musicMenu
        y: 0
        width: Constants.width
        height: Constants.height
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter

        Image {
            id: image
            x: 0
            y: -3
            width: 1280
            height: 400
            visible: false
            source: controller.songUrl
            fillMode: Image.PreserveAspectFit

            DesignEffect {
                id: designEffect1
                effects: [
                    DesignInnerShadow {}
                ]
            }
        }

        Rectangle {
            id: coverImageContainer
            y: 0
            width: 200
            height: coverImageContainer.width
            visible: false
            color: "#762f2f"
            clip: true
            anchors.horizontalCenter: parent.horizontalCenter

            Image {
                id: coverImage

                x: 0
                y: 26

                width: 200
                height: 200
                visible: true
                anchors.verticalCenter: parent.verticalCenter
                source: controller.songUrl
                clip: false
                anchors.horizontalCenter: parent.horizontalCenter
                fillMode: Image.PreserveAspectFit
            }
        }

        Slider {
            id: customSlider
            x: 0
            y: 264
            width: 200
            height: 20
            visible: true
            value: controller.songPercent
            // Initial value (0.0 to 1.0)

            // Custom styling
            background: Rectangle {
                x: customSlider.leftPadding
                y: customSlider.topPadding + customSlider.availableHeight / 2 - height / 2
                width: customSlider.availableWidth
                height: 4 // Height of the slider track
                radius: 2
                color: controller.songColorAvg // Empty/background color

                // This is the filled portion
                Rectangle {
                    width: customSlider.visualPosition * parent.width
                    height: parent.height
                    color: controller.songColorBright // Fill color
                    radius: 2
                }
            }

            // Custom handle (the part you drag)
            handle: Rectangle {
                id: rectangle1
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

        Row {
            id: musicSelectionThing
            x: 482
            y: 290
            width: skipButton.x + skipButton.width
            height: 45
            visible: false
            layoutDirection: Qt.LeftToRight

            RoundButton {
                id: backButton
                x: 617
                text: "+"
            }

            RoundButton {
                id: resumeButton
                x: 673
                text: "+"
            }

            RoundButton {
                id: skipButton
                x: 560
                text: "+"
            }
        }
    }

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
    }

    Image {
        id: image1
        x: 220
        y: 163
        width: 100
        height: 100
        visible: false
        source: controller.songUrl
        fillMode: Image.PreserveAspectFit
        DesignEffect {
            id: designEffect2
            effects: [
                DesignDropShadow {}
            ]
        }
    }

    states: [
        State {
            name: "SpotifyMenu"
            when: roundButtonSpotify.checked

            PropertyChanges {
                target: coverImageContainer
                x: 523
                y: 56
                width: 235
                height: coverImageContainer.width
                visible: true
                radius: 7
                clip: false
            }

            PropertyChanges {
                id: propertyChanges
                target: coverImage
                x: 523
                y: 59
                width: coverImageContainer.width
                height: coverImageContainer.height
                visible: true
                source: controller.songUrl
                clip: false
                baselineOffset: 0
                enabled: true
                smooth: true
                antialiasing: true
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 0
            }

            PropertyChanges {

                target: customSlider
                x: (parent.width - width) / 2 // This centers it horizontally
                y: 320
                width: 1103
                height: 20
                value: controller.songPercent
                anchors.horizontalCenterOffset: 0
                transformOrigin: Item.Center
            }

            PropertyChanges {
                target: musicSelectionThing
                x: (parent.width - width) / 2
                y: 346
                width: skipButton.x + skipButton.width
                height: 39
                visible: true
                anchors.horizontalCenterOffset: 5
                spacing: 50
            }

            PropertyChanges {
                target: musicMenu
                x: 89
                y: 0
                width: 1281
                height: 400
                anchors.horizontalCenterOffset: 0
            }

            PropertyChanges {
                target: image
                x: 0
                y: 0
                width: 1280
                height: 400
                visible: true
                scale: 1
                rotation: 180
                fillMode: Image.Stretch
            }

            PropertyChanges {
                target: designEffect1
                layerBlurRadius: 100
            }

            PropertyChanges {
                target: rectangle1
                visible: false
            }

            PropertyChanges {
                target: propertyChanges
                explicit: true
            }

            PropertyChanges {
                target: rectangle
                color: "#000000"
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
