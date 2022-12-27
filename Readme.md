
# Simple Spotify App
#https://developer.spotify.com/console/player/

This project was originally started to learn about about Oauth for authenitication. 
So the plan was to build a simply script that would be able to grab whatever song I was currently listenting to in Spotify. 
Well that portion ended up turning into a full blown module to interact with Spotify. 
I am currently building this for fun, and will use it as a base to learn more about various development task.


| Things To Explore\Learn |  
|-------------------------|
| CI/CD                   |
| Github Action           |
| Code Test               |
| Data Classes            |


| Things To Add             |  
|---------------------------|
| Robust token handling     |
| All Spotify Endpoints     |
| Result attributes         |
| Error Checking Throughout |

As this is a hobby project, it should work for the examples and the current endpoint built, but just keep in mind that 
this will get changed quite often as I continue to want to tinker with new things. 

Below are a few of the endpoints we support, and also an example script how how you can authenticate and start using the API. 

You can also fork this project and update the repoisitory secrets and use the provided runner, to communicate directly with Spotify.

**Example 1. Get currently playing song on Spotify.**

```python
from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
import pprint

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-currently-playing"])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
    playing = spotify_interact.spotify_currently_playing(realtime=True)
```

An example of the output is shown below, note the interval time is variable and can be changed using a different parameter. 

As shown above we use `realtime=True` this arguement takes a boolean. This will tell the module to keep printing any new songs
as they are returned from Spotify, using the interval specified. By deafault this is set to `realtime=False`.

https://user-images.githubusercontent.com/11384057/206332966-eb00adee-935c-4a31-8ba3-760701a1930d.mp4

**Example 2. Getting the audtio features for a given track ID.**

```python
from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
import pprint

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)

    playing = spotify_interact.spotify_track_audio_features(spotify_id="11dFghVXANMlKmJXsNCbNl")
    pprint.pprint(playing, compact=True)
```

Would return a dict object similar to what is shown below.

```commandline
{'acousticness': 0.011,                                                             
 'analysis_url': 'https://api.spotify.com/v1/audio-analysis/11dFghVXANMlKmJXsNCbNl',
 'danceability': 0.696,                                                             
 'duration_ms': 207960,                                                             
 'energy': 0.905,                                                                   
 'id': '11dFghVXANMlKmJXsNCbNl',                                                    
 'instrumentalness': 0.000905,
 'key': 2,
 'liveness': 0.302,
 'loudness': -2.743,
 'mode': 1,
 'speechiness': 0.103,
 'tempo': 114.944,
 'time_signature': 4,
 'track_href': 'https://api.spotify.com/v1/tracks/11dFghVXANMlKmJXsNCbNl',
 'type': 'audio_features',
 'uri': 'spotify:track:11dFghVXANMlKmJXsNCbNl',
 'valence': 0.625}

```

Currently Supported Endpoints Are Below


* [SpotifyApiBase](https://developer.spotify.com/documentation/web-api/)
* [SpotifyMe](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-current-users-profile)
* [SpotifyMePlaylist](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-list-of-current-users-playlists)
* [SpotifyCurrentlyPlaying](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-the-users-currently-playing-track)
* [SpotifyTopItems](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-users-top-artists-and-tracks)
* [SpotifyTrackAudioAnalysis](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-analysis)
* [SpotifyGetTracks](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks)
* [SpotifyGetUsersPlaylists](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-list-users-playlists)
* [SpotifyGetTrackAudioFeatures](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features)
* [SpotifyGetTracksAudioFeatures](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features)
* [SpotifyCreatePlaylist](https://developer.spotify.com/documentation/web-api/reference/#/operations/create-playlist)
* [SpotifyAddItemsToPlaylist](https://developer.spotify.com/documentation/web-api/reference/#/operations/add-tracks-to-playlist)
* [SpotifyGetPlaylist](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlist)
* [SpotifyGetPlaylistTracks](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlists-tracks)
* [SpotifyGetRecentlyPlayedTracks](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played)

Most methods if not all should have the proper docstrings and type checks.

