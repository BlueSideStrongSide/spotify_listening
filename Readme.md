
# Simple Spotify App
#https://developer.spotify.com/console/player/

This project was originally started to learn about about Oauth for authenitication. 
So the plan was to build a simply script that would be able to grab whatever song I was currently listenting to in Spotify. 
Well that portion ended up turning into a full blown module to interact with Spotify. 
I am currently building this for fun, and will use it as a base to learn more about various development task.


|  Things To Explore |  
|---|
|CI/CD |
|Github Action |
|Code Test |

As this is a hobby project, it should work for the examples and the current endpoint built, but just keep in mind that 
this will get changed quite often as I continue to want to tinker with new things. 

Below are a few of the endpoints we support, and also an example script how how you can authenticate and start using the API. 

You can also fork this project and update the repoisitory secrets and use the provided runner, to communicate directly with Spotify.

Example 1. If want to check what song is currently playing the script can be ran as shown below. 
```
from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
import pprint

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-currently-playing"])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
    playing = spotify_interact.spotify_currently_playing(realtime=True)
```

An example of the output is shown below, note the interval time is variable and can be changed using a different parameter. 


https://user-images.githubusercontent.com/11384057/206332966-eb00adee-935c-4a31-8ba3-760701a1930d.mp4


As shown above we use `realtime=True` This arguement takes a boolean. This will tell the module to keep printing any new songs
as they are returned from Spotify, using the interval specified. By deafault this is set to yes.

https://user-images.githubusercontent.com/6877923/115474571-03c75800-a23e-11eb-8096-8973aad5fa9f.mp4


Currently Supported Endpoints Are Below


* SpotifyApiBase
* SpotifyMe
* SpotifyMePlaylist
* SpotifyCurrentlyPlaying
* SpotifyTopItems
* SpotifyTrackAudioAnalysis
* SpotifyGetTracks
* SpotifyGetUsersPlaylists
* SpotifyGetTrackAudioFeatures
* SpotifyGetTracksAudioFeatures
* SpotifyCreatePlaylist
* SpotifyAddItemsToPlaylist
* SpotifyGetPlaylist
* SpotifyGetPlaylistTracks
* SpotifyGetRecentlyPlayedTracks
