from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_api import SpotifyHandler

spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'], enable_env_write=False)

if spotify_authenticator.authenticated:
    spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
    result = spotify_interact.spotify_get_recently_played_tracks()

    for track in result.tracks:
        print(f'Track Name: {track.track_name} Artist: {track.artist_name} Explicit: {str(track.explicit)}')
