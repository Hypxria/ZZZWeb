
import os
import sys
import dotenv
from pathlib import Path
import socket
from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from autogen.settings import url, import_paths
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PySide6.QtCore import QObject, Signal, Property, QTimer
from methods import *

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


class InformationBinding(QObject):
    xChanged = Signal()
    yChanged = Signal()
    heightChanged = Signal()
    songUrlChanged = Signal()
    songPercentChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._x = 29
        self._y = 200
        self._height = 600
        self._songUrl = sp_controller.getCoverImage()
        self._songPercent = sp_controller.getPlaybackProgressPercentage()
        print(self._songPercent)
        
        # Create Timer
        self.cover_timer = QTimer(self)
        self.cover_timer.setInterval(1000)  # Cover can update less frequently
        self.cover_timer.timeout.connect(self.updateCover)
        self.cover_timer.start()
        
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(50)  # More frequent progress updates
        self.progress_timer.timeout.connect(self.updateProgress)
        self.progress_timer.start()

    @Property(float, notify=songPercentChanged)
    def songPercent(self):
        return self._songPercent
    
    @songPercent.setter
    def songPercent(self, value):
        if self._songPercent != value:
            self._songPercent = value
            self.songPercentChanged.emit()
    
    @Property(str, notify=songUrlChanged)
    def songUrl(self):
        return self._songUrl
    
    @songUrl.setter
    def songUrl(self, value):
        if self._songUrl != value:
            self._songUrl = value
            self.songUrlChanged.emit()

    @Property(int, notify=xChanged)
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self._x != value:
            self._x = value
            self.xChanged.emit()

    @Property(int, notify=yChanged)
    def y(self):
        return self._y

    @y.setter   
    def y(self, value):
        if self._y != value:
            self._y = value
            self.yChanged.emit()
    
    @Property(int, notify=heightChanged)
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        if self._height != value:
            self._height = value
            self.heightChanged.emit()

    @Slot(int, int)
    def moveRectangle(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
    
    @Slot()
    def updateCover(self):
        new_url = sp_controller.getCoverImage()
        if new_url != self._songUrl:
            self._songUrl = new_url
            self.songUrlChanged.emit()
    
    @Slot()    
    def updateProgress(self):
        new_percent = sp_controller.getPlaybackProgressPercentage()
        if new_percent != self._songPercent:
            self._songPercent = new_percent
            self.songPercentChanged.emit()


            


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    controller = InformationBinding()
    engine.rootContext().setContextProperty("controller", controller)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())