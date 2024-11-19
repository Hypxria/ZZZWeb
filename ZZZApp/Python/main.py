import os
import sys
import dotenv
from pathlib import Path
import socket
from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QGuiApplication, QColor
from PySide6.QtQml import QQmlApplicationEngine
from autogen.settings import url, import_paths
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from methods import *
from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer
from dataclasses import dataclass

dotenv.load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SPOTIFY_SCOPES = [
    "ugc-image-upload", "user-read-playback-state", "user-modify-playback-state",
    "user-follow-modify", "user-read-private", "user-follow-read", "user-library-modify",
    "user-library-read", "streaming", "user-read-playback-position", "app-remote-control",
    "user-read-email", "user-read-currently-playing", "user-read-recently-played",
    "playlist-modify-private", "playlist-read-collaborative", "playlist-read-private",
    "user-top-read", "playlist-modify-public"
]

# Setting required variables to interact with Spotify API
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=",".join(SPOTIFY_SCOPES),
        client_id = SPOTIFY_CLIENT_ID,
        client_secret = SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://localhost:8888/callback"
    ),
    requests_timeout=300
)

sp_controller = SpotifyController(sp)
device_name = sp_controller.init_default_device(socket.gethostname().lower())


class InformationBinding(QObject):
    """Handles Spotify state management and UI updates"""
    
    # Signal definitions
    songUrlChanged = Signal()
    songPercentChanged = Signal()
    songColorAvgChanged = Signal()
    songColorBrightChanged = Signal()

    def __init__(self, spotifyController):
        super().__init__()
        self._spotifyController = spotifyController
        
        # Initialize state values
        self._songUrl = self._spotifyController.getCoverImage()
        self._songPercent = self._spotifyController.getPlaybackProgressPercentage()
        self._songColorAvg = self._spotifyController.get_average_hex_color(self._songUrl)
        
        
        self._setupTimers()

    def _setupTimers(self) -> None:
        """Setup and start update timers"""
        self._setupCoverTimer()
        self._setupProgressTimer()

    def _setupCoverTimer(self) -> None:
        """Setup timer for cover image updates"""
        self.coverTimer = QTimer(self)
        self.coverTimer.setInterval(1000)  # Update every second
        self.coverTimer.timeout.connect(self.updateCover)
        self.coverTimer.start()

    def _setupProgressTimer(self) -> None:
        """Setup timer for progress updates"""
        self.progressTimer = QTimer(self)
        self.progressTimer.setInterval(50)  # Update every 50ms
        self.progressTimer.timeout.connect(self.updateProgress)
        self.progressTimer.start()

    # Spotify Properties
    @Property(str, notify=songColorBrightChanged)
    def songColorBright(self) -> str:
        try:
            color = QColor(self._songColorAvg)
            h, s, l, _ = color.getHslF()
            brighter_color = QColor.fromHslF(
                h,
                s,
                min(1.0, l * 1.5),  # Increase lightness by 50%, cap at 1.0
                1.0
            )
            return brighter_color.name(QColor.HexRgb)
        except:
            return "#FFFFFF"  # Return white as fallback

    @songColorBright.setter
    def songColorBright(self, value: str) -> None:
        if self._songColorBright != value:
            self._songColorBright = value
            self.songColorBrightChanged.emit()
            
    @Property(str, notify=songColorAvgChanged)
    def songColorAvg(self) -> str:
        return self._songColorAvg
    
    @songColorAvg.setter
    def songColorAvg(self, value: str) -> None:
        if self._songColorAvg != value:
            self._songColorAvg = value
            self.songColorAvgChanged.emit()
    
    @Property(str, notify=songUrlChanged)
    def songUrl(self) -> str:
        return self._songUrl

    @songUrl.setter
    def songUrl(self, value: str) -> None:
        if self._songUrl != value:
            self._songUrl = value
            self.songUrlChanged.emit()

    @Property(float, notify=songPercentChanged)
    def songPercent(self) -> float:
        return self._songPercent

    @songPercent.setter
    def songPercent(self, value: float) -> None:
        if self._songPercent != value:
            self._songPercent = value
            self.songPercentChanged.emit()

    @Slot()
    def updateCover(self) -> None:
        """Update the cover image URL from Spotify"""
        try:
            newUrl = self._spotifyController.getCoverImage()
            if newUrl != self._songUrl:
                self.songUrl = newUrl
        except Exception as e:
            print(f"Error updating cover: {e}")

    @Slot()
    def updateProgress(self) -> None:
        """Update the song progress from Spotify"""
        try:
            newPercent = self._spotifyController.getPlaybackProgressPercentage()
            if newPercent != self._songPercent:
                self.songPercent = newPercent
        except Exception as e:
            print(f"Error updating progress: {e}")

    def cleanup(self) -> None:
        """Cleanup timers and resources"""
        self.coverTimer.stop()
        self.progressTimer.stop()


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # First create the Spotify controller
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=",".join(SPOTIFY_SCOPES),
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback"
        ),
        requests_timeout=300
    )
    
    sp_controller = SpotifyController(sp)
    device_name = sp_controller.init_default_device(socket.gethostname().lower())
    
    # Then pass it to InformationBinding
    controller = InformationBinding(sp_controller)
    engine.rootContext().setContextProperty("controller", controller)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
