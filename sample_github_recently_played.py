import datetime

from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'], enable_env_write=False)

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
    result = spotify_interact.spotify_get_recently_played_tracks()

    for track in result.tracks:
        if not track.explicit:
            with open("recently_played_tracks.txt", "a+") as out_file:
                out_file.write(f'GitHub_Runner_Date: {datetime.datetime.utcnow()} '
                    f'Track Name: "{track.track_name}" '
                    f'Artist Name: "{track.artist_name}" '
                    f'Web Link: {track.ext_spotify_url} ')
