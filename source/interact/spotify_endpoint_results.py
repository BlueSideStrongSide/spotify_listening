from typing import Type, List
from dataclasses import dataclass, field
import pprint
import source.interact.spotify_endpoints as sp_api

@dataclass
class SpotifyTrackResult:
    spotify_track: dict = field(default_factory=dict)

    @property
    def track_duration(self)->int:
        return int(self.spotify_track["duration_ms"])

    @property
    def album(self)-> str:
        return self.spotify_track["album"]

    @property
    def artists(self)-> list:
        return self.spotify_track["artists"]

    @property
    def track_name(self)-> list:
        return self.spotify_track["name"]

    @property
    def artist_name(self)-> list:
        return self.spotify_track["artists"][0]["name"]

    @property
    def artist_type(self)-> list:
        return self.spotify_track["artists"][0]["type"]

    @property
    def explicit(self)->bool:
        return self.spotify_track["explicit"]


@dataclass
class SpotifyResultApiBase:
    api_data: type[sp_api.SpotifyApiBase] = field(repr=False)
    response: dict = field(default_factory=dict)
    info_api: str = field(default_factory=str)
    show_sensitive_values: bool = True
    tracks: list[type[SpotifyTrackResult]] = field(default_factory=SpotifyTrackResult, init=False)

    def __post_init__(self):
        exempt = ["204 Nothing Is Currently Playing"]
        if self.response not in exempt:
            self.tracks = self._add_tracks()

    def replace_sensitive_values(self):
        ...

    def _add_tracks(self) -> List[type[SpotifyTrackResult]]:
        """
        Takes in a spotify response and look ino the item dictionary for a track key which will contain a list of all
        the returned spotify tracks.

        :return: List[type[SpotifyTrackResult]]
        """

        response_tracks: list[type[SpotifyTrackResult]] = []

        if self.response.get("items"):
            for item in self.response.get("items"):
                spotify_track = SpotifyTrackResult(spotify_track=item["track"])
                response_tracks.append(spotify_track)

        if self.response.get("tracks"):
            for item in self.response.get("tracks"):
                spotify_track = SpotifyTrackResult(spotify_track=item)
                response_tracks.append(spotify_track)

        return response_tracks

    def response_pretty(self):
        return pprint.pprint(self.response, indent=4, compact=True)

@dataclass
class SpotifyGetPlaylistTracksResult(SpotifyResultApiBase):

    @property
    def added_at(self) -> str:
        return self.response["items"][0]["added_at"]

    @property
    def added_by(self) -> str:
        return self.response["items"][0]["added_by"]

    @property
    def href(self) -> str:
        return self.response["href"]

    @property
    def spotify_user(self) -> dict:
        return self.response["items"][0]["added_by"]["href"]