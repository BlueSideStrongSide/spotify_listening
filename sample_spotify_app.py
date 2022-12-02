import datetime

from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
from datetime import date
import pprint

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played",'user-top-read'])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)

    playing = spotify_interact.spotify_get_recently_played_tracks()
    pprint.pprint(playing, compact=True)
