from rich import print
from spotipy import Spotify
import json

# catching errors
class InvalidSearchError(Exception):
    pass


def exit_application() -> None:
    
    # Exits the application
    
    print("[bold yellow]Exiting application...[/bold yellow]")
    import sys
    sys.exit(0)

class SpotifyController:
    
    # A controller class for interacting with the Spotify API.
    # This class provides methods for various Spotify operations such as
    # playing tracks, managing playlists, and controlling playback.
    

    def __init__(self, spotify: Spotify):
        # 
        # Vianney notes:
        # contructor class, is run the moment that sp_controller = SpotifyController(sp) in main
        #
        # Initialize the SpotifyController.
        #
        # Args:
        #     spotify (Spotify): An authenticated Spotify client object.
        # 
        self.spotify = spotify
        self.default_device_id = None

    def getPlaybackProgressPercentage(self) -> float:
        """
        Gets the current playback progress as a percentage.
    
        Returns:
            float: The percentage (0-100) of the way through the current track.
                   Returns 0 if no track is playing.
        """
        current_track = self.spotify.current_user_playing_track()
        
        if current_track is None or not current_track['is_playing']:
            return 0.0
            
        progress_ms = current_track['progress_ms']
        total_ms = current_track['item']['duration_ms']
        
        # Calculate percentage and round to 2 decimal places
        percentage = round(progress_ms / total_ms, 2)
        
        return percentage
    

    def add_current_song_to_playlist(self, playlist_name: str) -> None:
        # 
        # Adds the currently playing song to the specified playlist.

        # Args:
        #     playlist_name (str): The name of the playlist to add the song to.

        # Returns:
        #     None
        # 
        # Get the current song
        current_track = self.spotify.current_user_playing_track()
        if current_track is None:
            print("[bold red]No track is currently playing.[/bold red]")
            return

        track_uri = current_track['item']['uri']
        track_name = current_track['item']['name']

        # Get user's playlists
        playlists = self.spotify.current_user_playlists()
        
        # Find the specified playlist
        target_playlist = next((playlist for playlist in playlists['items'] if playlist['name'].lower() == playlist_name.lower()), None)
        
        if target_playlist is None:
            print(f"[bold red]Playlist '{playlist_name}' not found.[/bold red]")
            return

        # Add the track to the playlist
        self.spotify.user_playlist_add_tracks(self.spotify.me()['id'], target_playlist['id'], [track_uri])
        print(f"[bold green]Added '{track_name}' to playlist '{playlist_name}'.[/bold green]")


        def get_current_song(self) -> str:
                # 
                # Retrieves information about the currently playing song.

                # Returns:
                #     str: A string containing the track name and artist,
                #          or a message if no track is playing.
                # 
                current_track = self.spotify.current_user_playing_track()
                if current_track is not None and current_track['is_playing']:
                    track_name = current_track['item']['name']
                    artist_name = current_track['item']['artists'][0]['name']
                    return f"{track_name} by {artist_name}"
                else:
                    return "No track is currently playing."

    def play_previous_song(self) -> None:
            # 
            # Plays the previous song in the queue.

            # Returns:
            #     None
            # 
            self.spotify.previous_track(device_id=self.default_device_id)

    def get_album_uri(self, name: str) -> str:
            # 
            # Searches for and returns the Spotify URI for an album.

            # Args:
            #     name (str): The name of the album to search for.

            # Returns:
            #     str: The Spotify URI of the first matching album.

            # Raises:
            #     InvalidSearchError: If no album is found with the given name.
            # 
            results = self.spotify.search(q=name, type="album")
            if not results["albums"]["items"]:
                raise InvalidSearchError(f"No album found with name: {name}")
            return results["albums"]["items"][0]["uri"]

    def get_track_uri(self, name: str) -> str:
            # 
            # Searches for and returns the Spotify URI for a track.

            # Args:
            #     name (str): The name of the track to search for.

            # Returns:
            #     str: The Spotify URI of the first matching track.

            # Raises:
            #     InvalidSearchError: If no track is found with the given name.
            # 
            results = self.spotify.search(q=name, type="track")
            if not results["tracks"]["items"]:
                raise InvalidSearchError(f"No track found with name: {name}")
            return results["tracks"]["items"][0]["uri"]

    def get_artist_uri(self, name: str) -> str:
            # 
            # Searches for and returns the Spotify URI for an artist.

            # Args:
            #     name (str): The name of the artist to search for.

            # Returns:
            #     str: The Spotify URI of the first matching artist.

            # Raises:
            #     InvalidSearchError: If no artist is found with the given name.
            # 
            results = self.spotify.search(q=name, type="artist")
            if not results["artists"]["items"]:
                raise InvalidSearchError(f"No artist found with name: {name}")
            return results["artists"]["items"][0]["uri"]

    def play_album(self, uri: str) -> None:
            # 
            # Plays an album from its Spotify URI.

            # Args:
            #     uri (str): The Spotify URI of the album to play.

            # Returns:
            #     None
            # 
            self.spotify.start_playback(context_uri=uri, device_id=self.default_device_id)

    def play_track(self, uri: str) -> None:
            # 
            # Plays a track from its Spotify URI.

            # Args:
            #     uri (str): The Spotify URI of the track to play.

            # Returns:
            #     None
            # 
            self.spotify.start_playback(uris=[uri], device_id=self.default_device_id)

    def play_artist(self, uri: str) -> Spotify:
        # 
        # Plays an artist's top tracks from their Spotify URI.

        # Args:
        #     uri (str): The Spotify URI of the artist to play.

        # Returns:
        #     Spotify: The Spotify client object.
        # 
        self.spotify.start_playback(context_uri=uri, device_id=self.default_device_id)
        return self.spotify

    def play_playlist(self, playlist_id: str) -> Spotify:
        # 
        # Plays a playlist from its Spotify ID.

        # Args:
        #     playlist_id (str): The Spotify ID of the playlist to play.

        # Returns:
        #     Spotify: The Spotify client object.
        # 
        self.spotify.start_playback(context_uri=f"spotify:playlist:{playlist_id}", device_id=self.default_device_id)
        return self.spotify

    def next_track(self) -> Spotify:
        # 
        # Skips to the next track in the current playback queue.

        # Returns:
        #     Spotify: The Spotify client object.
        # 
        self.spotify.next_track(device_id=self.default_device_id)
        return self.spotify

    def pause_track(self) -> Spotify:
        # 
        # Pauses the currently playing track.

        # Returns:
        #     Spotify: The Spotify client object.

        # Note:
        #     If the track is already paused, a message will be printed.
        # 
        try:
            self.spotify.pause_playback(device_id=self.default_device_id)
            return self.spotify
        except Exception as e:
            if "Player command failed: Restriction violated" in str(e):
                print("[bold yellow]The track is already paused.[/bold yellow]")
            else:
                print(f"[bold red]An error occurred: {str(e)}[/bold red]")
            return self.spotify

    def resume_track(self) -> Spotify:
        # 
        # Resumes the currently paused track.

        # Returns:
        #     Spotify: The Spotify client object.

        # Note:
        #     If the track is already playing, a message will be printed.
        # 
        try:
            self.spotify.start_playback(device_id=self.default_device_id)
            return self.spotify
        except Exception as e:
            if "Player command failed: Restriction violated" in str(e):
                print("[bold yellow]The track is already playing.[/bold yellow]")
            else:
                print(f"[bold red]An error occurred: {str(e)}[/bold red]")
            return self.spotify

    def is_shuffle_on(self) -> bool:
        # 
        # Checks if shuffle mode is currently enabled.

        # Returns:
        #     bool: True if shuffle is on, False otherwise.

        # Note:
        #     If there's no active playback session, it returns False.
        # 
        playback_state = self.spotify.current_playback()
        if playback_state is not None:
            return playback_state['shuffle_state']
        else:
            print("[bold yellow]No active playback session.[/bold yellow]")
            return False

    def getCoverImage(self) -> str:
        """
        Gets the URL of the cover image for the currently playing track.
    
        Returns:
            str: URL of the album cover image. Returns empty string if no track is playing
                or no image is available.
        """
        current_track = self.spotify.current_user_playing_track()
        
        if current_track is None or not current_track['item']:
            return ""
            
        # Get album images array (contains different sizes)
        images = current_track['item']['album']['images']
        
        if not images:
            return ""
            
        # First image is typically the largest resolution
        # images[0] = large
        # images[1] = medium
        # images[2] = small
        return images[0]['url']
    
    

    def shuffle(self, state: str = None) -> None:
        # 
        # Toggles shuffle mode or sets it to a specific state.

        # Args:
        #     state (str, optional): The desired shuffle state ('on' or 'off').
        #         If not provided, the current state will be toggled.

        # Returns:
        #     None

        # Note:
        #     Prints a message indicating the new shuffle state.
        # 
        current_state = self.is_shuffle_on()
        
        if state is None:
            # Toggle shuffle
            new_state = not current_state
        else:
            # Set shuffle to specified state
            new_state = state.lower() == 'on'
        
        if new_state != current_state:
            self.spotify.shuffle(new_state, device_id=self.default_device_id)
            print(f"[bold green]Shuffle {'enabled' if new_state else 'disabled'}.[/bold green]")
        else:
            print(f"[bold yellow]Shuffle is already {'on' if new_state else 'off'}.[/bold yellow]")

    def change_volume(self, volume: int) -> Spotify:
        # 
        # Changes the volume of the playback.

        # Args:
        #     volume (int): The desired volume level (0-100).

        # Returns:
        #     Spotify: The Spotify client object.

        # Note:
        #     Prints a message confirming the new volume level.
        # 
        self.spotify.volume(volume, device_id=self.default_device_id)
        print(f"[bold green]Volume set to {volume}%[/bold green]")
        return self.spotify

    def repeat_track(self) -> Spotify:
        # 
        # Toggles repeat mode for the current track.

        # Returns:
        #     Spotify: The Spotify client object.

        # Note:
        #     Prints a message indicating the new repeat mode state.
        #     If there's no active playback session, a message will be printed.
        # 
        playback = self.spotify.current_playback()
        if playback:
            current_state = playback['repeat_state']
            new_state = 'track' if current_state != 'track' else 'off'
            self.spotify.repeat(new_state, device_id=self.default_device_id)
            print(f"[bold green]Repeat mode set to: {new_state}[/bold green]")
        else:
            print("[bold yellow]No active playback session.[/bold yellow]")
        return self.spotify

    def shuffle(self, state: str) -> Spotify:
        # 
        # Sets the shuffle state for the player.

        # Args:
        #     state (str): The desired shuffle state ('on' or 'off').

        # Returns:
        #     Spotify: The Spotify client object.

        # Note:
        #     Prints a message confirming the new shuffle state.
        # 
        state_bool = state.lower() == 'on'
        self.spotify.shuffle(state_bool, device_id=self.default_device_id)
        print(f"[bold green]Shuffle {'enabled' if state_bool else 'disabled'}.[/bold green]")
        return self.spotify

    def get_user_followed_artists(self) -> list:
        # 
        # Retrieves a list of artists the user is following.

        # Returns:
        #     list: A list of names of artists the user is following.

        # Note:
        #     This method handles pagination to retrieve all followed artists.
        # 
        artists = []
        results = self.spotify.current_user_followed_artists(limit=50)
        
        while results:
            for item in results['artists']['items']:
                artists.append(item['name'])
            if results['artists']['next']:
                results = self.spotify.next(results['artists'])
            else:
                results = None
        
        return artists

    def get_user_saved_tracks(self) -> list:
        # 
        # Retrieves a list of tracks saved in the user's library.

        # Returns:
        #     list: A list of strings, each containing a track name and its artist.

        # Note:
        #     This method handles pagination to retrieve all saved tracks.
        # 
        tracks = []
        results = self.spotify.current_user_saved_tracks(limit=50)
        
        while results:
            for item in results['items']:
                track = item['track']
                tracks.append(f"{track['name']} by {track['artists'][0]['name']}")
            if results['next']:
                results = self.spotify.next(results)
            else:
                results = None
        
        return tracks

    def get_user_playlists(self) -> tuple[list, list]:
        
        # Retrieves a list of the user's playlists.

        # Returns:
        #     tuple[list, list]: A tuple containing two lists:
        #         - The first list contains playlist names.
        #         - The second list contains corresponding playlist IDs.

        # Note:
        #     This method handles pagination to retrieve all user playlists.
        
        playlists = []
        playlist_ids = []
        results = self.spotify.current_user_playlists(limit=50)
        
        while results:
            for item in results['items']:
                playlists.append(item['name'])
                playlist_ids.append(item['id'])
            if results['next']:
                results = self.spotify.next(results)
            else:
                results = None
        
        return playlists, playlist_ids

    def init_default_device(self, local_device) -> str:
        # Initializes the default device for playback.

        # Args:
        #     local_device: The local device information.

        # Returns:
        #     str: The name of the initialized default device.

        # Note:
        #     This method searches for available devices and sets the default device
        #     based on the provided local device information.
        results = self.spotify.devices()

        device_name = None
        for device in results["devices"]:
            if device["name"].lower() == local_device:
                self.default_device_id = device["id"]
                device_name = device["name"]
                #print("Default device detected: " + device_name)
                break
            else:
                print("Default device not found, pick one from these")
                for i, device in enumerate(results["devices"], 1):
                    print(f"{i}. {device['name']}")
                    # Completing later- lunch ended
                print(len(results['devices']))
                choice = int(input("Enter the number of the device: "))
                selectedDevice = results['devices'][choice - 1]
                self.default_device_id = selectedDevice["id"]
                device_name = selectedDevice["name"]
                print(self.default_device_id)       
                print(device_name)
                break 
        return device_name