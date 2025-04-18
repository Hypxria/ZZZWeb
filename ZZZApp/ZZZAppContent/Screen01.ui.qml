

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
    color: "#ffffff"

    GroupItem {
        id: musicMenu
        y: 0
        width: 640
        height: Constants.height
        anchors.left: parent.left
        anchors.leftMargin: 0
        transformOrigin: Item.Left

        Image {
            id: imageBGSmall
            x: 0
            y: 0
            width: 640
            height: 400
            visible: true
            source: controller.songUrl
            rotation: 180
            mirror: true
            transformOrigin: Item.Center
            fillMode: Image.Stretch
            DesignEffect {
                id: designEffect2
                layerBlurRadius: 100
            }
        }

        Image {
            id: imageBGFull
            x: 0
            y: 0
            width: 1281
            height: 400
            visible: false
            transformOrigin: Item.Center
            fillMode: Image.PreserveAspectFit

            DesignEffect {
                id: designEffect1
                layerBlurRadius: 100
            }
        }

        Rectangle {
            id: rectangle3
            x: 0
            y: 0
            width: 640
            height: 400
            opacity: 0.6
            visible: true
            color: "#000000"
        }

        LyricsDisplay {
            id: lyricsDisplay
            width: 200
            height: 200
            visible: false
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -306
            anchors.horizontalCenterOffset: 418
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Connections {
            target: controller
            function onWindowLoaded() {
                controller.loadLyrics()
            }
        }

        Rectangle {
            id: coverImageContainer
            width: 235
            height: 235
            opacity: 1
            visible: true
            color: "#762f2f"
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: -31
            anchors.horizontalCenterOffset: 0
            clip: false
            anchors.horizontalCenter: parent.horizontalCenter

            Rectangle {
                id: rectangle2
                y: 0
                width: 235
                height: 235
                visible: true
                color: "#ffffff"
                radius: 10
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
                anchors.bottomMargin: 0

                Image {
                    id: image1
                    width: 235
                    height: 235
                    visible: true
                    anchors.verticalCenter: parent.verticalCenter
                    source: controller.songUrl
                    anchors.verticalCenterOffset: 0
                    anchors.horizontalCenterOffset: 0
                    anchors.horizontalCenter: parent.horizontalCenter
                    fillMode: Image.PreserveAspectFit
                }
            }

            Text {
                id: songTitle
                x: (parent.width - width) / 2
                y: 237
                visible: true
                color: "#ffffff"
                text: controller.songTitle
                anchors.bottom: parent.bottom
                anchors.bottomMargin: -21
                font.pixelSize: 15
                horizontalAlignment: Text.AlignHCenter
                font.family: "Urbanist ExtraBold"
            }

            GroupItem {
                id: group
                width: creatorNameBaseState.width + creationDateBaseState.width
                height: creatorNameBaseState.height
                anchors.top: creatorName.top
                anchors.topMargin: -1
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    id: creatorNameBaseState
                    x: 0
                    y: 0
                    visible: true
                    color: "#ffffff"
                    text: controller.songArtist + ' · '
                    anchors.top: coverImageContainer.bottom
                    anchors.topMargin: 20
                    font.pixelSize: 14
                    font.family: "Urbanist"
                    Text {
                        id: creationDateBaseState
                        x: parent.width
                        visible: true
                        color: "#ffffff"
                        text: controller.releaseYear
                        font.pixelSize: 14
                        font.family: "Urbanist"
                    }
                }
            }

            Text {
                id: creatorName
                x: 0
                y: 241
                visible: false
                text: controller.songArtist + ' · '
                anchors.left: parent.left
                anchors.top: coverImageContainer.bottom
                anchors.leftMargin: -38
                anchors.topMargin: 20
                font.pixelSize: 14
                font.family: "Urbanist"

                Text {
                    id: creationDate
                    x: parent.width
                    visible: true
                    text: controller.releaseYear
                    font.pixelSize: 14
                    font.family: "Urbanist ExtraBold"
                }
            }
        }

        Slider {
            id: customSlider
            x: 44
            y: 320
            width: 551
            height: 20
            visible: true
            value: controller.songPercent
            live: true
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
                visible: false
                radius: 8
                color: customSlider.pressed ? "#f0f0f0" : "#ffffff"
                border.color: "#1db954"
                border.width: 0
            }
        }

        Row {
            id: musicSelectionThing
            width: skipButton.x + skipButton.width
            height: 45
            visible: true
            anchors.top: customSlider.bottom
            anchors.topMargin: -2
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 25
            layoutDirection: Qt.LeftToRight

            RoundButton {
                id: backButton
                x: 617
                text: "+"

                Connections {
                    target: backButton
                    onClicked: controller.backSong()
                }
            }

            RoundButton {
                id: resumeButton
                x: 673
                text: "+"

                Connections {
                    target: resumeButton
                    onClicked: controller.pauseResume()
                }
            }

            RoundButton {
                id: skipButton
                x: 560
                text: "+"

                Connections {
                    target: skipButton
                    onClicked: controller.frontSong()
                }
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

    states: [
        State {
            name: "SpotifyMenuLyrics"
            when: roundButtonSpotify.checked

            PropertyChanges {
                target: coverImageContainer
                x: 523
                y: 63
                width: 216
                height: 216
                opacity: 1
                visible: true
                color: "#00762f2f"
                radius: 7
                anchors.verticalCenterOffset: -29
                clip: false
                anchors.horizontalCenterOffset: -438
            }

            PropertyChanges {
                target: customSlider
                x: (parent.width - width) / 2
                y: 320
                width: 1103
                height: 20
                value: controller.songPercent
                transformOrigin: Item.Center
                anchors.horizontalCenterOffset: 0
            }

            PropertyChanges {
                target: musicSelectionThing
                x: (parent.width - width) / 2
                y: 346
                width: skipButton.x + skipButton.width
                height: 39
                visible: true
                spacing: 50
                anchors.horizontalCenterOffset: 5
            }

            PropertyChanges {
                target: musicMenu
                x: 89
                y: 0
                width: 1280
                height: 400
                anchors.horizontalCenterOffset: 0
            }

            PropertyChanges {
                target: imageBGFull
                x: 0
                y: 0
                source: controller.songUrl
                transformOrigin: Item.Center
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
                target: rectangle
                color: "#000000"
            }

            PropertyChanges {
                target: songTitle
                x: image1.x
                y: 210
                color: "#ffffff"
                text: controller.songTitle
                anchors.bottomMargin: -24
                font.pixelSize: 19
                horizontalAlignment: Text.AlignLeft
                transformOrigin: Item.Left
                font.styleName: "Regular"
                font.family: "Urbanist ExtraBold"
                anchors.horizontalCenterOffset: -11
            }

            PropertyChanges {
                target: creationDate
                x: creatorName.width
                y: 0
                color: "#ffffff"
                text: controller.releaseYear
                font.pixelSize: 16
                font.family: "Urbanist"
            }

            PropertyChanges {
                target: creatorName
                x: 100
                y: 304
                visible: true
                color: "#ffffff"
                anchors.leftMargin: 0
                anchors.rightMargin: 0
                anchors.topMargin: 24
                anchors.bottomMargin: 76
                font.pixelSize: 16
                transformOrigin: Item.Left
                font.family: "Urbanist"
            }

            PropertyChanges {
                target: rectangle2
                x: 0
                y: 16
                opacity: 1
                color: "#ffffff"
                radius: 10
            }

            PropertyChanges {
                target: rectangle3
                x: 0
                y: 0
                width: 1281
                height: 400
                opacity: 0.6
                visible: true
                color: "#000000"
            }

            PropertyChanges {
                target: lyricsDisplay
                x: 639
                y: 121
                width: 784
                height: 100
                visible: true
                anchors.verticalCenterOffset: -36
                anchors.horizontalCenterOffset: 106
            }

            PropertyChanges {
                target: image1
                x: 0
                y: 0
                width: parent.width
                height: parent.height
                scale: 1
                transformOrigin: Item.Left
            }

            PropertyChanges {
                target: imageBGSmall
                visible: false
            }

            PropertyChanges {
                target: creatorNameBaseState
                visible: false
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
