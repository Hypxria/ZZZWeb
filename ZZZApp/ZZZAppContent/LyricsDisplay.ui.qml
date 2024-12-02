// LyricsDisplay.qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: lyricsContainer
    color: "transparent"

    Column {
        anchors.fill: parent
        spacing: 20

        Text {
            id: previousLine
            width: parent.width
            color: controller.songColorBright
            opacity: 0.5
            font.pixelSize: 18
            horizontalAlignment: Text.AlignHCenter
            text: controller.previousLyric
        }

        Text {
            id: currentLine
            width: parent.width
            color: controller.songColorBright
            font.pixelSize: 24
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            text: controller.currentLyric

            Behavior on text {
                PropertyAnimation {
                    target: currentLine
                    property: "opacity"
                    from: 0.5
                    to: 1.0
                    duration: 250
                }
            }
        }

        Text {
            id: nextLine
            width: parent.width
            color: controller.songColorBright
            opacity: 0.5
            font.pixelSize: 18
            horizontalAlignment: Text.AlignHCenter
            text: controller.nextLyric
        }
    }
}
