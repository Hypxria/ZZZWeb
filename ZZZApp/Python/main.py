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
    requests_timeout=10
)

sp_controller = SpotifyController(sp)
print('initing')
sp_controller.init_default_device(socket.gethostname().lower())
print('stuck?')


class InformationBinding(QObject):
    # Handles Spotify state management and UI updates
    
    # Signal definitions
    songUrlChanged = Signal()
    songPercentChanged = Signal()   
    songColorAvgChanged = Signal()
    songColorBrightChanged = Signal()
    songTitleChanged = Signal()
    songArtistChanged = Signal()
    releaseYearChanged = Signal()
    lyricsChanged = Signal()
    currentTimeChanged = Signal()
    currentLyricChanged = Signal()
    nextLyricChanged = Signal()
    previousLyricChanged = Signal()
    
    windowLoaded = Signal()



    def __init__(self, spotifyController):
        super().__init__()
        self._spotifyController = spotifyController
        
        # Initialize state values
        original_url = self._spotifyController.getCoverImage()
        self._songUrl = self._processAndRoundImage(original_url)
        self._songPercent = self._spotifyController.getPlaybackProgressPercentage()
        self._songColorAvg = self._spotifyController.get_average_hex_color(original_url)
        self._original_url = None  
        self._songTitle = ""
        self._songArtist = ""
        self._releaseYear = ""
        
        # Initialize lyrics state
        self._currentLyric = ""
        self._nextLyric = ""
        self._previousLyric = ""
        self._lyrics = []
        self._current_track_id = None  # Add track ID tracking

        # Timers
        self._lyricTimer = QTimer(self)  # Pass self as parent
        self._lyricTimer.setInterval(100)  # 100ms interval
        self._lyricTimer.timeout.connect(self.updateLyricDisplay)
        
        self._songCheckTimer = QTimer(self)
        self._songCheckTimer.setInterval(1000)  # Check every second
        self._songCheckTimer.timeout.connect(self.checkSongChange)
        self._songCheckTimer.start()
        
        QTimer.singleShot(100, self.windowLoaded.emit)

        self._setupTimers()

    # Setup and preperation functions

    def _setupTimers(self) -> None:
        # Setup and start update timers
        self._setupCoverTimer()
        self._setupProgressTimer()
        self._setupInformationTimer()
        self._setupLyricsTimer()

    def _setupCoverTimer(self) -> None:
        # Setup timer for cover image updates
        self.coverTimer = QTimer(self)
        self.coverTimer.setInterval(500)  # Update every second
        self.coverTimer.timeout.connect(self.updateCover)
        self.coverTimer.start()

    def _setupProgressTimer(self) -> None:
        # Setup timer for progress updates
        self.progressTimer = QTimer(self)
        self.progressTimer.setInterval(100)  # Update every 50ms
        self.progressTimer.timeout.connect(self.updateProgress)
        self.progressTimer.start()
    
    def _setupLyricsTimer(self) -> None:
        # Setup timer for lyrics updates
        self.lyricsTimer = QTimer(self)
        self.lyricsTimer.setInterval(100)  # Update every second
        self.lyricsTimer.timeout.connect(self.updateLyricDisplay)
        self.lyricsTimer.start()
        
        # Add song change check timer
        self._songCheckTimer = QTimer(self)
        self._songCheckTimer.setInterval(1000)  # Check every second
        self._songCheckTimer.timeout.connect(self.checkSongChange)
        self._songCheckTimer.start()
    
    def _setupInformationTimer(self) -> None:
        # Set up timer for updating song information
        self._infoTimer = QTimer()
        self._infoTimer.setInterval(500)  # Update every second
        self._infoTimer.timeout.connect(self.updateSongInformation)
        self._infoTimer.start()
    
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
            
    # Song Information
    @Property(str, notify=songTitleChanged)
    def songTitle(self) -> str:
        return self._songTitle

    @songTitle.setter
    def songTitle(self, value: str) -> None:
        if self._songTitle != value:
            self._songTitle = value
            self.songTitleChanged.emit()

    @Property(str, notify=songArtistChanged)
    def songArtist(self) -> str:
        return self._songArtist

    @songArtist.setter
    def songArtist(self, value: str) -> None:
        if self._songArtist != value:
            self._songArtist = value
            self.songArtistChanged.emit()

    @Property(str, notify=releaseYearChanged)
    def releaseYear(self) -> str:
        return self._releaseYear

    @releaseYear.setter
    def releaseYear(self, value: str) -> None:
        if self._releaseYear != value:
            self._releaseYear = value
            self.releaseYearChanged.emit()
    
    @Property(str, notify=songUrlChanged)
    def songUrl(self) -> str:
        return self._songUrl

    @songUrl.setter
    def songUrl(self, value: str) -> None:
        if value and self._songUrl != value:
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

    @Property(list, notify=lyricsChanged)
    def lyrics(self):
        return self._lyrics
        
    @lyrics.setter
    def lyrics(self, value):
        if self._lyrics != value:
            self._lyrics = value
            self.lyricsChanged.emit()
    
    @Property(int, notify=currentTimeChanged)
    def currentTime(self):
        return self._currentTime
        
    @currentTime.setter
    def currentTime(self, value):
        if self._currentTime != value:
            self._currentTime = value
            self.currentTimeChanged.emit()
    @Property(str, notify=currentLyricChanged)
    def currentLyric(self):
        return self._currentLyric

    @currentLyric.setter
    def currentLyric(self, value):
        if self._currentLyric != value:
            self._currentLyric = value
            self.currentLyricChanged.emit()

    @Property(str, notify=nextLyricChanged)
    def nextLyric(self):
        return self._nextLyric

    @nextLyric.setter
    def nextLyric(self, value):
        if self._nextLyric != value:
            self._nextLyric = value
            self.nextLyricChanged.emit()

    @Property(str, notify=previousLyricChanged)
    def previousLyric(self):
        return self._previousLyric

    @previousLyric.setter
    def previousLyric(self, value):
        if self._previousLyric != value:
            self._previousLyric = value
            self.previousLyricChanged.emit()
    
    @Slot()
    def checkSongChange(self):
        """Check if the song has changed and reload lyrics if needed"""
        try:
            playback = self._spotifyController.spotify.current_playback()
            if not playback or not playback.get('item'):
                return

            current_track_id = playback['item']['id']
            
            # If track has changed, reload lyrics
            if current_track_id != self._current_track_id:
                print("Song changed, reloading lyrics...")
                self._current_track_id = current_track_id
                self.loadLyrics()
                
        except Exception as e:
            print(f"Error checking song change: {e}")


    @Slot()
    def updateSongInformation(self):
        """Update current song information and check for song changes"""
        try:
            playback = self._spotifyController.spotify.current_playback()
            if not playback or not playback.get('item'):
                return

            # Get current track info
            current_track = playback['item']
            current_track_id = current_track['id']
            
            # Update song title and artist
            self.songTitle = current_track['name']
            self.songArtist = current_track['artists'][0]['name']

            # Check if song has changed
            if current_track_id != self._current_track_id:
                print(f"Song changed to: {self.songTitle} by {self.songArtist}")
                self._current_track_id = current_track_id
                
                # Update cover image
                self.updateCover()
                
                # Load new lyrics
                self.loadLyrics()
                
                # Update progress
                self.updateProgress()

        except Exception as e:
            print(f"Error updating song information: {e}")

    
    @Slot()
    def updateLyricDisplay(self):
        """Update the displayed lyrics based on current playback position"""
        try:
            playback = self._spotifyController.spotify.current_playback()
            if not playback or not self._lyrics:
                return

            current_time = playback['progress_ms']
            
            # Find current lyric position
            current_index = -1
            for i, lyric in enumerate(self._lyrics):
                if lyric['time'] <= current_time:
                    current_index = i
                else:
                    break

            if current_index >= 0:
                # Set previous lyric
                if current_index > 0:
                    self.previousLyric = self._lyrics[current_index - 1]['words']
                else:
                    self.previousLyric = ""

                # Set current lyric
                self.currentLyric = self._lyrics[current_index]['words']

                # Set next lyric
                if current_index < len(self._lyrics) - 1:
                    self.nextLyric = self._lyrics[current_index + 1]['words']
                else:
                    self.nextLyric = ""
            else:
                # Before first lyric
                self.previousLyric = ""
                self.currentLyric = self._lyrics[0]['words'] if self._lyrics else ""
                self.nextLyric = self._lyrics[1]['words'] if len(self._lyrics) > 1 else ""

        except Exception as e:
            print(f"Error updating lyrics display: {e}")


    
    @Slot()
    def loadLyrics(self):
        """Load lyrics for current song"""
        try:
            lyrics_data = self._spotifyController.getLyrics()
            if lyrics_data and lyrics_data.get('synced'):
                self._lyrics = lyrics_data['synced']
                self._lyricTimer.start()
                # Reset lyrics display
                self.previousLyric = ""
                self.currentLyric = "Loading lyrics..."
                self.nextLyric = ""
            else:
                self._lyrics = []
                self._lyricTimer.stop()
                self.previousLyric = ""
                self.currentLyric = "No lyrics available"
                self.nextLyric = ""
        except Exception as e:
            print(f"Error loading lyrics: {e}")
            self.currentLyric = "Error loading lyrics"

    def setSpotifyController(self, controller):
        """Set the Spotify controller instance"""
        self._spotifyController = controller
        # Start the lyrics system
        self.loadLyrics()


    
    # Value Updaters

    @Slot()
    def updateLyricDisplay(self):
        """Update the displayed lyrics based on current playback position"""
        try:
            playback = self._spotifyController.spotify.current_playback()
            if not playback or not self._lyrics:
                return

            current_time = playback['progress_ms']
            
            # Find current lyric position
            current_index = -1
            for i, lyric in enumerate(self._lyrics):
                if lyric['time'] <= current_time:
                    current_index = i
                else:
                    break

            if current_index >= 0:
                # Set previous lyric
                if current_index > 0:
                    self.previousLyric = self._lyrics[current_index - 1]['words']
                else:
                    self.previousLyric = ""

                # Set current lyric
                self.currentLyric = self._lyrics[current_index]['words']

                # Set next lyric
                if current_index < len(self._lyrics) - 1:
                    self.nextLyric = self._lyrics[current_index + 1]['words']
                else:
                    self.nextLyric = ""
            else:
                # Before first lyric
                self.previousLyric = ""
                self.currentLyric = self._lyrics[0]['words'] if self._lyrics else ""
                self.nextLyric = self._lyrics[1]['words'] if len(self._lyrics) > 1 else ""

        except Exception as e:
            print(f"Error updating lyrics display: {e}")


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
                if self._spotifyController.get_average_hex_color(new_url) != '':                    
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
            if newPercent != self._songPercent and newPercent != 0:
                self.songPercent = newPercent
                print(f"Progress updated to: {self._songPercent * 100}%")
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
    
    print('here?')
    # First create the Spotify controller
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=",".join(SPOTIFY_SCOPES),
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback"
        ),
        requests_timeout=10
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
