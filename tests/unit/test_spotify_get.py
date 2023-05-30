import pytest
import json
from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow
from source.interact.spotify_endpoint_results import  SpotifyTrackResult
from source.interact.spotify_api import SpotifyHandler

@pytest.fixture
def sample_track_data():
    with open("sample_track.json", 'r') as f:
        data = json.load(f)

    return data

def test_offline_get_tracks(sample_track_data):
    result_track = [x for x in sample_track_data["tracks"]]
    assert len(result_track) == 3

def test_offline_get_tracks_track_handler(sample_track_data):
    result_track = [SpotifyTrackResult(x) for x in sample_track_data["tracks"]]
    assert result_track[0].track_name == "Knights of Cydonia"
    assert result_track[1].track_name == "Uprising"
    assert result_track[2].track_name == "Time is Running Out"

@pytest.fixture(scope="module")
def spotify_interact():
    spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=["user-read-recently-played", 'user-top-read'], enable_env_write=False)
    if spotify_authenticator.authenticated:
        return SpotifyHandler(auth_manager=spotify_authenticator)

def test_live_get_tracks(spotify_interact):
    result = spotify_interact.spotify_get_tracks(ids="7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B")
    assert len(result.tracks) == 3

def test_live_get_playlist(spotify_interact):
    result = spotify_interact.spotify_get_playlist(playlist_id="3cEYpjA9oz9GiPac4AsH4n")
    assert result.response.get("description") == 'A playlist for testing pourposes'

def test_live_get_audio_features(spotify_interact):
    result = spotify_interact.spotify_track_audio_features(spotify_id="11dFghVXANMlKmJXsNCbNl")
    assert result.response.get("instrumentalness") == 0.000905


if __name__ == '__main__':
    print("Local Testing")