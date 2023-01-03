from dataclasses import dataclass, field

@dataclass
class SpotifyApiBase:
    required_0auth: bool = True
    realtime : bool = False
    generate_qr: bool = False
    parameters: bool = False
    data: bool = False
    required_scope: str = ""
    data_parameters: dict = field(default_factory=dict)
    query_parameters: str = field(default_factory=str)
    interval: int = field(default_factory=int)
    method: str = field(default_factory=str)
    follow_next : bool = False
    follow_next_results : str = ""
    api_endpoint: str = field(default_factory=str)
    info_api: str = field(default_factory=str)
    info_exception: str = field(default_factory=str)
    access_token: str = field(default_factory=str)
    headers: dict = field(default_factory=dict)
    info_api = "https://developer.spotify.com/documentation/web-api/"
    info_exception = "General Exception For The Requested Endpoint See Documentation For Details"

@dataclass
class SpotifyMe(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "me/"
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-current-users-profile"

@dataclass
class SpotifyMePlaylist(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "me/playlists"
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-list-of-current-users-playlists"

@dataclass
class SpotifyCurrentlyPlaying(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "me/player/currently-playing"
    custom_options = ['interval', 'realtime', 'generate_qr']
    interval :int = 30
    realtime : bool = False
    generate_qr : bool = True
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-the-users-currently-playing-track"

@dataclass
class SpotifyTopItems(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "me/top/{top_type}"
    required_scope = "user-top-read"
    allowed_variable_type: list = field(default_factory=lambda: ['artists', 'tracks'] )
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-users-top-artists-and-tracks"
    info_exception : str = f'This endpoint only allows "artits" or "tracks" for the wanted top type'

@dataclass
class SpotifyTrackAudioAnalysis(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "audio-analysis/{spotify_id}"
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-analysis"
    info_exception : str = f'This endpoint only allows a proper Spotify ID please see the documentation for more examples'

@dataclass
class SpotifyGetTracks(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "tracks"
    parameters : bool = True
    query_parameters_list: list = field(default_factory=lambda: ["ids","market"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks"
    info_exception : str = f'This endpoint only allows a list of track ids, no more than 50 at a time. Please see the documentation for more examples'

@dataclass
class SpotifyGetUsersPlaylists(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "users/{user_id}/playlists"
    parameters : bool = True
    query_parameters_list: list = field(default_factory=lambda: ["limit","offset"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-list-users-playlists"
    info_exception : str = f'This endpoint only allows a list of track ids, no more than 100 at a time. Please see the documentation for more examples'

@dataclass
class SpotifyGetTrackAudioFeatures(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "audio-features/{spotify_id}"
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features"
    info_exception : str = f'This endpoint only allows a proper Spotify ID please see the documentation for more examples'

@dataclass
class SpotifyGetTracksAudioFeatures(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "audio-features"
    parameters : bool = True
    query_parameters_list: list = field(default_factory=lambda: ["ids"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features"
    info_exception : str = f'This endpoint only allows a proper Spotify ID please see the documentation for more examples'

@dataclass
class SpotifyCreatePlaylist(SpotifyApiBase):
    method : str = "POST"
    api_endpoint : str = "users/{user_id}/playlists"
    required_scope = "playlist-modify-public,playlist-modify-private"
    data: bool = True
    data_parameters: dict = field(default_factory=lambda: {"name":"","description":"","public":""})
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features"
    info_exception : str = f'This endpoint only allows a proper Spotify ID please see the documentation for more examples'

@dataclass
class SpotifyAddItemsToPlaylist(SpotifyApiBase):
    method : str = "POST"
    api_endpoint : str = "playlists/{playlist_id}/tracks"
    data: bool = True
    data_parameters: dict = field(default_factory=lambda: {"uris": [], "position": ""})
    required_scope = "playlist-modify-public,playlist-modify-private"
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/add-tracks-to-playlist"
    info_exception : str = f'This endpoint only allows a proper Playlist ID please see the documentation for more examples'

@dataclass
class SpotifyGetPlaylist(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "playlists/{playlist_id}"
    parameters: bool = True
    query_parameters_list: list = field(default_factory=lambda: ["fields","additional_types", "market"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlist"
    info_exception : str = f'This endpoint only allows a proper Playlist ID please see the documentation for more examples'

@dataclass
class SpotifyGetPlaylistTracks(SpotifyApiBase):
    method : str = "GET"
    api_endpoint : str = "playlists/{playlist_id}/tracks"
    required_scope = "playlist-modify-public,playlist-modify-private"
    parameters :bool = True
    query_parameters_list: list = field(default_factory=lambda: ["fields", "limit", "offset","additional_types"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlists-tracks"
    info_exception : str = f'This endpoint only gets the tracks for a provided Playlist ID'

@dataclass
class SpotifyGetRecentlyPlayedTracks(SpotifyApiBase):
    method : str = "GET"
    required_scope :str = "user-read-recently-played"
    api_endpoint : str = "me/player/recently-played"
    follow_next : bool = True
    follow_next_results: list = field(default_factory=lambda: [])
    parameters :bool = True
    query_parameters_list: list = field(default_factory=lambda: ["after","before","limit"])
    info_api : str = "https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played"
    info_exception : str = f'Get tracks from the current user\'s recently played tracks. Note: Currently doesn\'t support podcast episodes.'


