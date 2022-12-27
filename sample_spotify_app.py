from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler
import pprint
import json

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'])

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)

    playing = spotify_interact.spotify_get_playlist(playlist_id="4kAqBBEZQsBIXMIJl6u8tO")
    print(playing)

    # for song in playing['items']:
    #     print(f'Artist: {song["track"]["artists"][0]["name"]} --> Song: {song["track"]["name"]} --> Played_at: {song["played_at"]}')
        # pprint.pprint(song, indent=2, compact=True)
