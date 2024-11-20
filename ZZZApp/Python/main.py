import os
import sys
import dotenv
from pathlib import Path
import socket
from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer
from PySide6.QtGui import QGuiApplication, QColor
from PySide6.QtQml import QQmlApplicationEngine
from autogen.settings import url, import_paths
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from methods import *
from UtilityMethods import *


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
_utilities = utilityMethods()
device_name = sp_controller.init_default_device(socket.gethostname().lower())


class InformationBinding(QObject):
    # Handles Spotify state management and UI updates
    
    # Signal definitions
    songUrlChanged = Signal()
    songPercentChanged = Signal()
    songColorAvgChanged = Signal()
    songColorBrightChanged = Signal()

    def __init__(self, spotifyController):
        super().__init__()
        self._spotifyController = spotifyController
        
        # Initialize state values
        original_url = self._spotifyController.getCoverImage()
        self._songUrl = self._processAndRoundImage(original_url)
        self._songPercent = self._spotifyController.getPlaybackProgressPercentage()
        self._songColorAvg = self._spotifyController.get_average_hex_color(original_url)
        self._original_url = None  
        
        self._setupTimers()

    def _setupTimers(self) -> None:
        # Setup and start update timers
        self._setupCoverTimer()
        self._setupProgressTimer()

    def _setupCoverTimer(self) -> None:
        # Setup timer for cover image updates
        self.coverTimer = QTimer(self)
        self.coverTimer.setInterval(50)  # Update every second
        self.coverTimer.timeout.connect(self.updateCover)
        self.coverTimer.start()

    def _setupProgressTimer(self) -> None:
        # Setup timer for progress updates
        self.progressTimer = QTimer(self)
        self.progressTimer.setInterval(50)  # Update every 50ms
        self.progressTimer.timeout.connect(self.updateProgress)
        self.progressTimer.start()
        
    def _processAndRoundImage(self, url):
        if not url:
            return ""
        try:
            print("Starting image processing...")
            output_path = os.path.abspath(f"rounded_cover_{hash(url)}.png")
            
            if url.startswith('file:///'):
                print(f"Already a file URL, skipping: {url}")
                return url
                
            print(f"Processing URL: {url}")
            rounded_url = utilityMethods.create_rounded_image_from_url(url, output_path)
            
            if rounded_url is None:
                print(f"Failed to process image, falling back to original URL: {url}")
                return url
                
            file_url = QUrl.fromLocalFile(rounded_url).toString()
            print(f"Final file URL: {file_url}")
            return file_url
            
        except Exception as e:
            print(f"Error in _process_and_round_image: {e}")
            return url
    
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
        # Update the cover image URL from Spotify
        try:
            new_url = self._spotifyController.getCoverImage()
            # Only process if the original URL changed
            if new_url != self._original_url:
                self._original_url = new_url  # Store original URL
                rounded_url = self._processAndRoundImage(new_url)
                
                
                self.songUrl = rounded_url
                # Update color using ORIGINAL URL, not the processed file URL
                self._songColorAvg = self._spotifyController.get_average_hex_color(new_url)
                self.songColorAvgChanged.emit()
                self.songColorBrightChanged.emit()
                
        except Exception as e:
            print(f"Error updating cover: {e}") 

    @Slot()
    def updateProgress(self) -> None:
        # Update the song progress from Spotify
        try:
            newPercent = self._spotifyController.getPlaybackProgressPercentage()
            if newPercent != self._songPercent:
                self.songPercent = newPercent
                print(f"Progress updated to: {self._songPercent}%")
        except Exception as e:
            print(f"Error updating progress: {e}")

    def cleanup(self) -> None:
    # Stop timers first
        self.coverTimer.stop()
        self.progressTimer.stop()
        
        # Clean up rounded image cache
        try:
            cache_pattern = "rounded_cover_*.png"
            cache_files = list(Path().glob(cache_pattern))
            print(f"Cleaning up {len(cache_files)} cache files...")
            
            for file in cache_files:
                try:
                    file.unlink()
                    print(f"Deleted cache file: {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
                    
        except Exception as e:
            print(f"Error during cache cleanup: {e}")






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

    app.aboutToQuit.connect(controller.cleanup)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
