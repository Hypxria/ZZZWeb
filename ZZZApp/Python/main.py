import os
import sys
from pathlib import Path
import dotenv
import socket

from PySide6.QtCore import QObject, Slot, Property, Signal, QTimer, QThread, QEvent
from PySide6.QtGui import QGuiApplication, QColor
from PySide6.QtQml import QQmlApplicationEngine

from autogen.settings import url, import_paths
from spotipy.oauth2 import SpotifyOAuth
import spotipy

import time
import threading
from typing import Optional, Callable
import logging

from methods import *
from UtilityMethods import *

debug = False

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

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


class WindowEventFilter(QObject):
    def __init__(self, information_binding):
        super().__init__()
        self._information_binding = information_binding
        self._move_timer = QTimer()
        self._move_timer.setSingleShot(True)
        self._move_timer.timeout.connect(self._on_move_finished)
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Move:
            # Window is being moved
            if not hasattr(self._information_binding, '_is_moving'):
                self._information_binding._is_moving = True
                # Pause updates during movement
                if hasattr(self._information_binding, '_lyricTimer'):
                    self._information_binding._lyricTimer.stop()
                if hasattr(self._information_binding, 'progressTimer'):
                    self._information_binding.progressTimer.stop()
            
            # Restart the timer each time we move
            self._move_timer.start(100)
            
        return super().eventFilter(obj, event)
    
    def _on_move_finished(self):
        # Movement has stopped
        self._information_binding._is_moving = False
        # Resume updates
        if hasattr(self._information_binding, '_lyricTimer'):
            self._information_binding._lyricTimer.start()
        if hasattr(self._information_binding, 'progressTimer'):
            self._information_binding.progressTimer.start()


class SpotifyEventListener(threading.Thread):
    def __init__(self, spotify, callback: Callable, interval: float = 1.0):
        super().__init__()
        self.spotify = spotify
        self.callback = callback
        self.interval = interval
        self.last_playback_state: Optional[dict] = None
        self._running = True
        self.daemon = True  # Thread will exit when main program exits

    def run(self):
        while self._running:
            try:
                current_playback = self.spotify.current_playback()
                
                if current_playback != self.last_playback_state:
                    if self._has_relevant_changes(current_playback):
                        # Get additional track details including release date
                        if current_playback and current_playback.get('item'):
                            track_id = current_playback['item']['id']
                            track_details = self.spotify.track(track_id)
                            # Add release date to playback info
                            current_playback['track_details'] = {
                                'release_date': track_details['album']['release_date']
                            }
                        self.callback(current_playback)
                    
                self.last_playback_state = current_playback
                
            except Exception as e:
                print(f"Error in event listener: {e}")
            
            time.sleep(self.interval)


    def _has_relevant_changes(self, current_playback: Optional[dict]) -> bool:
        if not current_playback or not self.last_playback_state:
            return True

        # Check for track change
        current_track = current_playback.get('item', {}).get('id')
        last_track = self.last_playback_state.get('item', {}).get('id')
        if current_track != last_track:
            return True

        # Check for playback state change (playing/paused)
        current_playing = current_playback.get('is_playing')
        last_playing = self.last_playback_state.get('is_playing')
        if current_playing != last_playing:
            return True

        return False

    def stop(self):
        self._running = False


class ImageProcessor(QThread):
    finished = Signal(str, str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self._spotifyController = sp_controller
        self._image_processor = None
        

        
    def run(self):
        # Update the cover image URL from Spotify
        try:
            new_url = self._spotifyController.getCoverImage()
            # Only process if the original URL changed
            if new_url != self.url:
                rounded_url = self._processAndRoundImage(new_url)
                self.finished.emit(rounded_url, new_url)                    
        except Exception as e:
            print(f"Error updating cover: {e}") 
    
    def _processAndRoundImage(self, url):
        if not url:    
            default_image_path = os.path.abspath("default_cover.png")
            print(f"Using default image: {default_image_path}")
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
        
        # For optimization
        self._is_moving = False
        self._move_timer = QTimer()
        self._move_timer.setSingleShot(True)
        self._move_timer.timeout.connect(self._onMoveFinished)
        
        # Reduce update frequency
        self._update_throttle = {}

        
        # Initialize state values
        original_url = self._spotifyController.getCoverImage()
        self._songUrl = self._processAndRoundImage(original_url)
        self._songPercent = self._spotifyController.getPlaybackProgressPercentage()
        self._songColorAvg = self._spotifyController.get_average_hex_color(original_url)
        self._original_url = None  
        self._songTitle = ""
        self._songArtist = ""
        self._releaseYear = ""
        
        self._image_processor = None
        
        self._event_listener = None
        self.start_event_listener()

        
        # Start Debug Mode
        self._debug = False
        
        # Initialize lyrics state
        self._currentLyric = ""
        self._nextLyric = ""
        self._previousLyric = ""
        self._lyrics = []
        self._current_track_id = None  # Add track ID tracking
        
        QTimer.singleShot(100, self.windowLoaded.emit)

        self._setupTimers()

    # Setup and preperation functions
    
    def moveStarted(self):
        """Call this when window starts moving"""
        self._is_moving = True
        # Pause non-essential updates
        if hasattr(self, '_lyricTimer'):
            self._lyricTimer.stop()
        
    def moveStopped(self):
        """Call this when window stops moving"""
        # Don't immediately resume - wait a short moment
        self._move_timer.start(100)  # 100ms delay
        
    def _onMoveFinished(self):
        self._is_moving = False
        # Resume updates
        if hasattr(self, '_lyricTimer'):
            self._lyricTimer.start()
            
    def _throttle(self, key, interval):
        """Helper to throttle frequent updates"""
        now = time.time()
        if key in self._update_throttle:
            if now - self._update_throttle[key] < interval:
                return True
        self._update_throttle[key] = now
        return False
    
    def start_event_listener(self):
        self._event_listener = SpotifyEventListener(
            self._spotifyController.spotify,
            self._handle_playback_event
        )
        self._event_listener.start()
    
    def _handle_playback_event(self, playback_state):
        """Handle playback state changes"""
        if not playback_state:
            return

        try:
            current_track = playback_state.get('item', {})
            if not current_track:
                return

            track_id = current_track.get('id')
            if track_id != self._current_track_id:
                # Track changed
                self._current_track_id = track_id
                
                # Update song information
                self.songTitle = current_track.get('name', '')
                print(self.songTitle)   
                artists = current_track.get('artists', [])
                self.songArtist = artists[0].get('name', '') if artists else ''
                
                album = current_track.get('album', {})
                self.releaseYear = album.get('release_date', '')
                self.releaseYear = self.releaseYear.split('-')[0] if self.releaseYear else ''
                print(self.releaseYear)

                # Update cover
                self._updateCover()
                
                # Load new lyrics
                self.loadLyrics()

            # Update playback progress
            self.updateProgress()

        except Exception as e:
            print(f"Error handling playback event: {e}")


    def _setupTimers(self) -> None:
        # Setup and start update timers
        self._setupProgressTimer()
        self._setupLyricsTimer()
        

        # Create image processor
        self._imageProcessor = ImageProcessor(self._spotifyController)
        self._imageProcessor.finished.connect(self._onCoverProcessed)

    def _setupProgressTimer(self) -> None:
        # Setup timer for progress updates
        self._progressThread = QThread()
        # Thread New

        self.progressTimer = QTimer(self)
        self.progressTimer.setInterval(500)  # Update every 50ms
        self.progressTimer.timeout.connect(self.updateProgress)
        self.progressTimer.start()

        self._progressThread.started.connect(self.progressTimer.start)
        self._progressThread.finished.connect(self.progressTimer.stop)
    
    def _setupLyricsTimer(self) -> None:
        # Setup timer for lyrics updates
        self._lyricsThread = QThread()
        # Thread New
        
        self.lyricsTimer = QTimer(self)
        self.lyricsTimer.setInterval(500)  # Update every second
        self.lyricsTimer.timeout.connect(self.updateLyricDisplay)
        self.lyricsTimer.start()
        
        self._lyricsThread.started.connect(self.lyricsTimer.start)
        self._lyricsThread.finished.connect(self.lyricsTimer.stop)

    
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
    
    def _onCoverProcessed(self, processed_url, original_url):
        try:
            self.songUrl = processed_url
            self._original_url = original_url
            
            # Update color using original URL
            if self._spotifyController.get_average_hex_color(original_url) != '':
                self._songColorAvg = self._spotifyController.get_average_hex_color(original_url)
                self.songColorAvgChanged.emit()
                self.songColorBrightChanged.emit()
        except Exception as e:
            print(f"Error updating cover: {e}")

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
            
    
    # Modifier Functions
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
                self._updateCover()
                
                # Load new lyrics
                self.loadLyrics()
                
                # Update progress
                self.updateProgress()

        except Exception as e:
            print(f"Error updating song information: {e}")

    @Slot()
    def pauseResume(self):
        """Pause or resume playback"""
        try:
            playback = self._spotifyController.spotify.current_playback()
            if not playback:
                return

            if playback['is_playing']:
                self._spotifyController.spotify.pause_playback()
            else:
                self._spotifyController.spotify.start_playback()

        except Exception as e:
            print(f"Error pausing/resuming playback: {e}")
    
    @Slot()
    def backSong(self):
        """Go back to the previous song"""
        try:
            progress = self._spotifyController.spotify.current_playback()['progress_ms']
            if progress['progress_ms'] > 3000:
                self._spotifyController.spotify.seek_track(0)
            self._spotifyController.spotify.previous_track()
        except Exception as e:
            print(f"Error going back to previous song: {e}")
    
    @Slot()
    def frontSong(self):
        """Skip to the next song"""
        try:
            self._spotifyController.spotify.next_track()
        except Exception as e:
            print(f"Error skipping to next song: {e}")
            
    @Slot()
    def loadLyrics(self):
        if self._is_moving:
            return
            
        # Throttle updates
        if self._throttle('lyrics', 0.1):  # 100ms minimum between updates
            return
            
        try:
            playback = self._spotifyController.spotify.current_playback()

            lyrics_data = self._spotifyController.getLyrics()
            if lyrics_data and lyrics_data.get('synced'):
                self._lyrics = lyrics_data['synced']
                
                # Reset lyrics display
                if hasattr(self, '_lyricTimer') and not self._lyricTimer.isActive():
                    self._lyricTimer.start()
                    
                #reset lyrics
                self.previousLyric = ""
                self.currentLyric = "Loading lyrics..."
                self.nextLyric = ""
            else:
                self._lyrics = []
                if hasattr(self, '_lyricTimer'):
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
            if hasattr(self, '_is_moving') and self._is_moving:
                print('"Skipping lyric update due to slider movement." (self._is_moving')
                return
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
    def _updateCover(self):
        try:
            if hasattr(self, '_is_moving') and self._is_moving:
                return
            new_url = self._spotifyController.getCoverImage()
            if new_url != self._original_url:
                # Clean up completed threads
                print("Before processor check")  # Debug print
                if self._image_processor is not None:
                    print('Cleaning up old processor')
                    self._image_processor.quit()
                    self._image_processor.wait()
                    self._image_processor.deleteLater()
                print('Creating new processor')
                # Create new processor
                self._image_processor = ImageProcessor(self._original_url)
                self._image_processor.finished.connect(self._onCoverProcessed)
                self._image_processor.start()
                print('post2')
        except Exception as e:
            print(f"Error in _updateCover: {e}")
            print(f"Error location: {e.__traceback__.tb_lineno}")


    def _cleanup_processor(self, processor):
        if processor in self._image_processor:
            processor.quit()
            processor.wait()
            self._image_processor.remove(processor)
            processor.deleteLater()

    @Slot()
    def updateProgress(self) -> None:
        # Update the song progress from Spotify
        try:
            if hasattr(self, '_is_moving') and self._is_moving:
                return
            if hasattr(self, '_lyricTimer') and not self._lyricTimer.isActive():
                self._lyricTimer.start()
            newPercent = self._spotifyController.getPlaybackProgressPercentage()
            if newPercent != self._songPercent and newPercent != 0:
                self.songPercent = newPercent
                if self._debug:
                    print(f"Progress updated to: {self._songPercent * 100}%")
        except Exception as e:
            print(f"Error updating progress: {e}")

    def cleanup(self) -> None:
    # Stop timers first
        
        if hasattr(self, '_imageProcessor'):
            self._imageProcessor.quit()
            self._imageProcessor.wait()
        
        if hasattr(self, '_lyricsThread'):
            self._lyricsThread.quit()
            self._lyricsThread.wait()
        
        if hasattr(self, '_progressThread'):
            self._progressThread.quit()
            self._progressThread.wait()
            
        self._image_processor = None


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
    
    if debug:
        logger.debug("Starting lyric display update")
        sp_controller = SpotifyController(sp)
        try:
            sp_controller.init_default_device(socket.gethostname().lower())
            logger.debug("Completed lyric display update")
        except Exception as e:
            logger.error(f"Error updating lyrics display: {e}", exc_info=True)
    else:
        sp_controller = SpotifyController(sp)
        sp_controller.init_default_device(socket.gethostname().lower())

    
    # Then pass it to InformationBinding
    controller = InformationBinding(sp_controller)
    engine.rootContext().setContextProperty("controller", controller)
    
    event_filter = WindowEventFilter(controller)

    app.aboutToQuit.connect(controller.cleanup)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if engine.rootObjects():
        root_window = engine.rootObjects()[0]
        root_window.installEventFilter(event_filter)
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
