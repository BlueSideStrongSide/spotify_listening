

import asyncio
import aiohttp
import requests
import json
import pprint
import json
import inspect
import source.interact.spotify_endpoints as sp_api
from source.qr_generate import generate_spotify_qr
from source.util.logger.logger import SpotifyLogger
from source.auth.spotify_oauth_authorization import OauthSpotify_Authorization_Code_Flow


class SpotifyInternalHelper(SpotifyLogger):

    def __init__(self):
        super().__init__()

        self._auth_manager = None
        self._headers = None
        self._resp = None


    def default_headers(self):
        return  {"Authorization": f'Bearer {self._auth_manager._access_token}',"Content-Type": "application/json"}

    async def _build_request(self, format_api_endpoint_parameters:dict,
                             auth_manager: OauthSpotify_Authorization_Code_Flow,
                             headers:dict =None) -> dict:
        """
        :param format_api_endpoint_parameters: API specific endpoint paramaters to communicated with the wanted endpoint
        :param auth_manager: passed from sister class should not need direct interaction
        :param headers: must be a dict with a key 'headers' and within that dict is another dict with the headers wanted
        :return: a dict containing the api response
        """

        self._auth_manager = auth_manager
        self._headers = headers or self.default_headers
        self._current_endpoint = format_api_endpoint_parameters['api_endpoint']

        format_api_endpoint_parameters["api_endpoint"] = f"https://api.spotify.com/v1/{format_api_endpoint_parameters['api_endpoint']}"

        api_result = await self._make_request(prepared_api_endpoint_parameters=format_api_endpoint_parameters)

        return api_result

    async def _make_request(self, prepared_api_endpoint_parameters:dict,api_response=None):

        with requests.session() as s:
            while True:
                do_action = getattr(s,prepared_api_endpoint_parameters["method"].lower())

                self._resp = do_action(prepared_api_endpoint_parameters["api_endpoint"],
                                 headers=self.default_headers())

                if self._resp.status_code == 200:
                    self.api_response = json.loads(self._resp.content.decode())
                    asyncio.create_task(self._update_logging())

                    if prepared_api_endpoint_parameters.get("realtime"):
                        await self.realtime_process_response()

                if self._resp.status_code == 204:
                    self.api_response = f"{self._resp.status_code} Nothing Is Currently Playing"
                    self.logger.debug(f'{self.api_response}')

                if self._resp.status_code == 401:
                    self.api_response = f"{self._resp.status_code} Access Token Is Not Valid"
                    self.logger.debug(f'{self.api_response}')

                    await self._auth_manager._third_request_refreshed_access_token()

                if not prepared_api_endpoint_parameters.get("realtime"):
                    return self.api_response

                await asyncio.sleep(prepared_api_endpoint_parameters.get("interval"))

    async def _build_request_v2(self, format_api_endpoint_parameters:sp_api.SpotifyApiBase,
                             auth_manager: OauthSpotify_Authorization_Code_Flow,
                             headers:dict =None) -> dict:
        """
        :param format_api_endpoint_parameters: API specific endpoint paramaters to communicated with the wanted endpoint
        :param auth_manager: passed from sister class should not need direct interaction
        :param headers: must be a dict with a key 'headers' and within that dict is another dict with the headers wanted
        :return: a dict containing the api response
        """

        self._auth_manager = auth_manager
        self._headers = headers or self.default_headers
        self._current_endpoint = format_api_endpoint_parameters.api_endpoint

        format_api_endpoint_parameters.api_endpoint = f"https://api.spotify.com/v1/{self._current_endpoint}"

        api_result = await self._make_request_v2(prepared_api_endpoint_parameters=format_api_endpoint_parameters)

        return api_result

    async def _make_request_v2(self, prepared_api_endpoint_parameters:sp_api.SpotifyApiBase,
                               api_response=None,
                               follow_next:bool=False):

        with requests.session() as s:

            # print(prepared_api_endpoint_parameters) # <-- DEBUG Print

            while True:
                do_action = getattr(s,prepared_api_endpoint_parameters.method.lower())

                self._resp = do_action(prepared_api_endpoint_parameters.api_endpoint,
                                       headers=self.default_headers(),
                                params=prepared_api_endpoint_parameters.query_parameters,
                               data=prepared_api_endpoint_parameters.data_parameters)

                self.logger.debug(f'{self._resp.status_code} {self._resp.url}')#<-- Debug Printer

                if self._resp.status_code == 200 or self._resp.status_code == 201:
                    self.api_response = json.loads(self._resp.content.decode())
                    asyncio.create_task(self._update_logging())

                    if prepared_api_endpoint_parameters.realtime:
                        await self.realtime_process_response()

                    # if prepared_api_endpoint_parameters.follow_next and self.api_response["next"]:
                    #     captured_responses = [self.api_response]
                    #     counter = 0
                    #
                    #     self.logger.debug("Follwing Pagination to gather all items")
                    #     print(self.api_response["next"], self.api_response["cursors"])
                    #     self.logger.debug("NEXT URL ABOVE")
                    #
                    #     pag_result = do_action(self.api_response["next"],
                    #               headers=self.default_headers())
                    #
                    #     print(pag_result)
                    #
                    #     return json.loads(pag_result.content.decode())



                if self._resp.status_code == 204:
                    self.api_response = f"{self._resp.status_code} Nothing Is Currently Playing"

                if self._resp.status_code == 401:
                    self.api_response = f"{self._resp.status_code} Access Token Is Not Valid"
                    self.logger.debug(f'{self.api_response}')
                    await self._auth_manager._third_request_refreshed_access_token()

                if self._resp.status_code == 403:
                    self.api_response = f"Http_Status:{self._resp.status_code} More than likely required scopes are missing review documentation"

                if self._resp.status_code ==400 or self._resp.status_code ==404:
                    self.api_response = f'Http_Status: {self._resp.status_code} Request failed confirm API parameters are correct you requrested --> {self._resp.url} ' \
                                        f'Review the info section for endpoint settings {prepared_api_endpoint_parameters.info_api}'

                if not prepared_api_endpoint_parameters.realtime:
                    return self.api_response

                await asyncio.sleep(prepared_api_endpoint_parameters.interval)

    async def realtime_process_response(self):

        trimmed_out = f"HTTP_Status_Code {self._resp.status_code} Runner_Timestamp:'{self._auth_manager.current_time_fmt}' Artist: '{self.api_response['item']['artists'][0]['name']}' Song: '{self.api_response['item']['name']}' API_timestamp: {self.api_response['timestamp']}"

        self.logger.debug(f'{trimmed_out}')

    async def _update_logging(self):
        track_logging = ["me/player/currently-playing"]

        if self._current_endpoint in track_logging:
            with open("listening_spotify_api_dump.log", "a+") as out:
                pprint.pprint(self.api_response, compact=True, indent=0, stream=out)

            with open("trim_output.log", "w+") as out:
                out.write(f"Artist: '{self.api_response['item']['artists'][0]['name']}' Song: '{self.api_response['item']['name']}'")

            track_url = self.api_response['item']['external_urls']['spotify']

            await generate_spotify_qr.SpotifyQRGenerator(spotify_url=track_url).generate_qr(qr_save_path="spotify.png")


class SpotifyHandler(SpotifyLogger):

    def __init__(self, auth_manager: OauthSpotify_Authorization_Code_Flow):
        super().__init__()

        self._auth_manager = auth_manager
        self._internals = SpotifyInternalHelper()
        self._api_requested = None
        self.api_response = None

    @property
    def api_requested(self):
        return self._api_requested

    @api_requested.setter
    def api_requested(self, a):
        self._api_requested = a

        #Update/Validate/Prepare
        self._api_requested.access_token = self._auth_manager._access_token

        #Make Request To API
        self.request(v2_data=self._api_requested)

    def _spotify_scope_validation(self, scope:str):
        self.logger.debug("Checking if needed scope is in Auth Manager")
        for needed_scope  in scope.split(','):
            if needed_scope not in self._auth_manager._scope.split(' '):
                raise Exception(f"You do not have the needed scopes to work with this Endpoint '{needed_scope}' is missing")

    def _update_query_parameters(self, provided_args=None,api_settings=None):

        api_settings.query_parameters = [f'{api_settings.query_parameters}{parameter}={provided_args.get(parameter)}'
                                         for parameter in api_settings.query_parameters_list if
                                         provided_args.get(parameter)]

        return '&'.join(api_settings.query_parameters)

    def _update_data_parameters(self):
        ...

    def request(self,v2_data:sp_api =None):

        self.api_response = asyncio.run(self._internals._build_request_v2(format_api_endpoint_parameters=v2_data,
                                                             auth_manager=self._auth_manager))

    def spotify_currently_playing(self,realtime:bool =False,interval:int =30) -> dict:
        """

        :param realtime: module will periodically check the spotify API and return the result immediately to the term.
        :param interval: The delay in seconds to wait between making another request
        :return: If used with realtime nothing is returned, without realtime the response is a dict of the spotify response
        """
        #Grab Settings
        api_settings = sp_api.SpotifyCurrentlyPlaying()

        #need to dynamically take arguments and update API dataclass
        api_settings.realtime = realtime
        api_settings.interval = interval

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_me(self) -> dict:
        """
        Get detailed profile information about the current user (including the current user's username).

        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyMe()

        # Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_me_playlist(self, playlist_name:str ="") -> dict:
        """
        Get a list of the playlists owned or followed by the current Spotify user.
        :param playlist_name: Playlist name within the spotify account
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyMePlaylist()

        # can we create one function to validate for each API?
        #need to dynamically take arguments and update API dataclass

        #Setter will validate and make request to API
        self.api_requested = api_settings

        if playlist_name:
            for playlist in self.api_response["items"]:
                if playlist.get("name").lower() == playlist_name.lower():
                    self.api_response = playlist

        return self.api_response

    def spotify_get_tracks(self,spotify_ids:str) -> dict:
        """
        Get Spotify catalog information for multiple tracks based on their Spotify IDs.
        :param spotify_ids: comma seperated list of track ids
        :return: If used with realtime nothing is returned, without realtime the response is a dict of the spotify response
        """
        api_settings = sp_api.SpotifyGetTracks()

        #can we create one function to validate for each API?
        if len(spotify_ids.split()) <= 50:
            api_settings.query_parameters = api_settings.query_parameters+spotify_ids
        else:
            raise Exception(api_settings.info_exception)

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_get_users_playlists(self,user_id:str) -> dict:
        """
        Get a list of the playlists owned or followed by a Spotify user.
        :param user_id: user ID as shown from the spotify API, use the spotify_me endpoint to determine if needed
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyGetUsersPlaylists()

        #can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{user_id}',user_id)

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_top_items(self,top_type:str) -> dict:
        """
        Get the current user's top artists or tracks based on calculated affinity.
        :param top_type: The correct top type, only valid options are "artists" and "tracks"
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyTopItems()

        if api_settings.required_scope:
            self._spotify_scope_validation(scope=api_settings.required_scope)

        # can we create one function to validate for each API?
        if top_type in api_settings.allowed_variable_type:
            api_settings.api_endpoint = api_settings.api_endpoint.replace('{top_type}',top_type)
        else:
            raise Exception(api_settings.info_exception)

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_track_audio_analysis(self,spotify_id:str,realtime: bool = False,interval:int = 5) -> dict:
        """
        Get a low-level audio analysis for a track in the Spotify catalog. The audio analysis describes the track’s structure and musical content, including rhythm, pitch, and timbre.
        :param spotify_id: the spotify track/episode ID as returned by the API
        :param realtime: If multiple IDs are submitted we will show you a real time print of the data as it is retunred
        :param interval:  THe time between each GET request, be kind to the spotify API.
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyTrackAudioAnalysis()

        # can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{spotify_id}',spotify_id)

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_track_audio_features(self,spotify_id:str) -> dict:
        """
        Get audio feature information for a single track identified by its unique Spotify ID.
        :param spotify_id:  the spotify track/episode ID as returned by the API
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyGetTrackAudioFeatures()

        # can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{spotify_id}',spotify_id)

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_tracks_audio_features(self,spotify_ids:str|list) -> dict:
        """
        Get audio features for multiple tracks based on their Spotify IDs.
        :param spotify_ids: a comma seperated list of multiple spotify IDs, this method will submit them all at once
        :return: Spotify API response for this endpoint
        """
        if isinstance(spotify_ids,list):
            spotify_ids = ','.join(spotify_ids)

        api_settings = sp_api.SpotifyGetTracksAudioFeatures()

        # can we create one function to validate for each API?
        api_settings.query_parameters = api_settings.query_parameters + spotify_ids

        #Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_create_playlist(self, userd_id:str, playlist_name: str, playlist_description:str, playlist_public:bool =False) -> dict:
        """
        Create a playlist for a Spotify user. (The playlist will be empty until you add tracks.)
        :param userd_id: The user ID as shown in the spotify API. Use the spotif_me method to determine.
        :param playlist_name: The name of the new spotify playlist
        :param playlist_description: The desciption of the new spotify playlist
        :param playlist_public: Should the playlist be public
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyCreatePlaylist()

        if api_settings.required_scope:
            self._spotify_scope_validation(scope=api_settings.required_scope)

        # can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{user_id}', userd_id)
        api_settings.data_parameters["name"] = playlist_name
        api_settings.data_parameters["description"] = playlist_description
        api_settings.data_parameters["public"] = playlist_public
        api_settings.data_parameters =  json.dumps(api_settings.data_parameters)

        # Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_add_items_to_playlist(self, playlist_id:str ,spotify_tracks:str|list , position:int = False) -> dict:
        """
        Add one or more items to a user's playlist.
        :param playlist_id: The ID of playlist to add the items to
        :param spotify_tracks: The list of spotify track_ids that will be added
        :param position: what position should the additions be inserted into, within the playlist
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyAddItemsToPlaylist()

        if api_settings.required_scope:
            self._spotify_scope_validation(scope=api_settings.required_scope)

        # can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{playlist_id}', playlist_id)

        correct_format = []
        if isinstance(spotify_tracks,list):
            for track in spotify_tracks:
                if track.startswith("spotify:track:"):
                    correct_format.append(track)
        else:
            for track in spotify_tracks.split(","):
                correct_format.append(f'spotify:track:{track}')

        api_settings.data_parameters["uris"] = correct_format
        api_settings.data_parameters =  json.dumps(api_settings.data_parameters)
        
        # Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_get_playlist_tracks(self, playlist_id:str, fields:str="") -> dict:
        """
        Get a playlist owned by a Spotify user.
        :param playlist_id: Spotify_ID of the playlist to grab the tracks
        :param fields: Filters for the query: a comma-separated list of the fields to return. If omitted, all fields are returned. For example, to get just the playlist''s description and URI: fields=description,uri. A dot separator can be used to specify non-reoccurring fields, while parentheses can be used to specify reoccurring fields within objects. For example, to get just the added date and user ID of the adder: fields=tracks.items(added_at,added_by.id). Use multiple parentheses to drill down into nested objects, for example: fields=tracks.items(track(name,href,album(name,href))). Fields can be excluded by prefixing them with an exclamation mark, for example: fields=tracks.items(track(name,href,album(!name,href)))
                       Example value:"items(track(id,name))"
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyGetPlaylistTracks()

        if api_settings.required_scope:
            self._spotify_scope_validation(scope=api_settings.required_scope)

        # can we create one function to validate for each API?
        api_settings.api_endpoint = api_settings.api_endpoint.replace('{playlist_id}', playlist_id)
        api_settings.query_parameters = f'{api_settings.query_parameters}{fields}'

        # Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response

    def spotify_get_recently_played_tracks(self, limit:int =20, after:int=0 , before:int=0) -> dict:
        """
        Spotify has a hard limit on 50 songs regardless of the before or after setting. You can only see 50 songs MAX

        :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
        :param after: A Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position. If after is specified, before must not be specified.
        :param before: A Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position. If before is specified, after must not be specified.
        :return: Spotify API response for this endpoint
        """
        api_settings = sp_api.SpotifyGetRecentlyPlayedTracks()

        if api_settings.required_scope:
            self._spotify_scope_validation(scope=api_settings.required_scope)

        # can we create one function to validate for each API?
        if api_settings.parameters:
            api_settings.query_parameters = self._update_query_parameters(provided_args=locals(), api_settings=api_settings)

        # Setter will validate and make request to API
        self.api_requested = api_settings

        return self.api_response


if __name__ == "__main__":
    spotify_authenticator = OauthSpotify_Authorization_Code_Flow(scopes=[])

    if spotify_authenticator.authenticated:
        spotify_interact = SpotifyHandler(auth_manager=spotify_authenticator)
        spotify_interact.spotify_currently_playing(realtime=True)
