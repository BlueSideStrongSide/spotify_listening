from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
import pprint

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
    new_playlist = spotify_interact.spotify_get_playlist_tracks(playlist_id="3wjg8guJFz1lbuPBXCizKj", limit=30)

    for track in new_playlist.tracks:
        print(track.artist_name,"-->" , track.track_name)


