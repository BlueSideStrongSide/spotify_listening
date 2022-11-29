import random
import os
import string
import time
import webbrowser

import dotenv
import requests
import asyncio
import http.server
import base64
import json

from urllib.parse import urlencode
from dotenv import load_dotenv, set_key, find_dotenv
from source.auth.local_http_server import MyRequestHandler as Custom_RequestHandler
from source.util.logger.logger import SpotifyLogger

BRUTE_ENV = dotenv.find_dotenv()
HOSTNAME = "localhost"
SERVERPORT = 8888


# @dataclass
# class SpotifyAuthSettings:
#     def __init__(self,scopes:list):
#
#         # This is not currently being used
#         self._client_id = os.getenv("_client_id")
#         self._client_secret = os.getenv("_client_secret")
#         self._redirect_uri = os.getenv("_redirect_uri")
#         self._refresh_token = os.getenv("_refresh_token")
#         self._auth_code = os.getenv("_auth_code")
#         self._access_token = os.getenv("_access_token")
#         self._expired_at = os.getenv("_expired_at")
#         self._auth_scopes = os.getenv("_scopes") or ' '.join(scopes)


class OauthSpotify_Authorization_Code_Flow(SpotifyLogger):

    def __init__(self, scopes:list, client_id:str =None, client_secret:str =None, login_redirect:str ="http://localhost:8888", local_test=None, enable_env_write:bool =True):
        """
        The login_redirect is currently locked to one port on local host http://localhost:8888, please ensure your spotify app is configured correctly.

        I will update this in a future release.

        :param scopes:required scopes for whatever endpoints you plan to communicate with. Review the documentation for more info
        :param client_id: Cli
        :param client_secret:
        :param local_test:
        """
        super().__init__() #<-- Init logger build out additional options if needed
        self._enable_env_write = enable_env_write
        self._load_env(scopes)
        self.__validate_env(client_id, client_secret, login_redirect)

        self.authenticated = False
        self._token_type = None
        self._expired = None

        self._client_state = ''.join(random.choices(string.ascii_letters+string.digits, k=16))
        self._local_http_server = http.server.HTTPServer((HOSTNAME, SERVERPORT), Custom_RequestHandler)
        self._local_http_server_wait = 10

        self.logger.debug("Hello From 0Auth Class")


        if not local_test:
            asyncio.run(self.auth_flow())

    def _load_env(self,p_scopes):
        try:
            load_dotenv(BRUTE_ENV)

            self._client_id = os.getenv("_client_id")
            self._client_secret = os.getenv("_client_secret")
            self._redirect_uri = os.getenv("_redirect_uri")
            self._refresh_token = os.getenv("_refresh_token")
            self._auth_code = os.getenv("_auth_code")
            self._access_token = os.getenv("_access_token")
            self._expired_at = os.getenv("_expired_at")
            self._auth_scopes = os.getenv("_scopes") or ' '.join(p_scopes)
        except Exception as e:
            self.logger.debug(f"Failed to load provided .env path review and update settings {BRUTE_ENV}")
            self.logger.debug(e)
            exit()

    def __validate_env(self,p_client_id, p_client_secret, p_login_redirect):
        required_settings = [self._client_id, self._client_secret, self._redirect_uri]
        provided_settings = [p_client_id, p_client_secret, p_login_redirect]

        if not os.path.exists(BRUTE_ENV) and self._enable_env_write:
            self.logger.debug("Please create at least a blank .env in your project directory")
            exit()
            # with open(BRUTE_ENV,'w+') as env:
            #     env.write("# Spotify_Sensitive_Settings")

        if not all(required_settings):
            self.logger.debug("Unable to find required settings")
            if all(provided_settings):
                try:
                    self.logger.debug("Attempting to store provided settings")
                    if self._enable_env_write:
                        set_key(BRUTE_ENV, "_client_id", p_client_id)
                        set_key(BRUTE_ENV, "_client_secret", p_client_secret)
                        set_key(BRUTE_ENV, "_redirect_uri", p_login_redirect)

                    self.logger.debug("Attempting to read after storing provided settings")

                    load_dotenv(BRUTE_ENV)
                    self._client_id = os.getenv("_client_id")
                    self._client_secret = os.getenv("_client_secret")
                    self._redirect_uri = os.getenv("_redirect_uri")
                except Exception as e:
                    self.logger.debug(f"Failed To Create .env and load settings {e}")
                    self.logger.debug(f"Failed To Create .env and load settings {BRUTE_ENV} {[setting for setting in provided_settings]}")
                    exit()
            else:
                self.logger.debug("Missing required settings and also provided settings are not correct program will exit.")
                self.logger.debug("If you are providing settings ensure they are formatted and correctly entered")
                exit()

    async def auth_flow(self):

        if not await self._auth_cache_available:
            self.logger.info("Auth Cache Is Not Available")
            await self._first_request_authorization()
            await self._second_request_access_token()
            await self._third_request_refreshed_access_token()

        self.logger.info("Requesting New Access Token")
        await self._third_request_refreshed_access_token()

        self.logger.debug("Token acquired with requested or cache scopes")
        self.authenticated = True

    @property
    async def _auth_cache_available(self):
        if self._refresh_token:
            return True
        else:
            return False

    @property
    def _cache_token_expired(self) ->bool:
        current_token_timer = self._expired_at or self._expired
        if current_token_timer:
            if time.time() > float(current_token_timer):
                self.logger.debug("Token Is Expired")
                return True
            else:
                return False

    @property
    def current_time_fmt(self):
        return time.strftime('%X')

    @property
    def _get_redirect_uri(self):
        return self._redirect_uri

    @property
    def build_authorization_string(self):
        encoded_string=f'{self._client_id}:{self._client_secret}'.encode("ascii")
        authorization_b64 = base64.b64encode(encoded_string).decode()

        return authorization_b64

    @property
    def _first_request_auth_params(self):

        parameters = {"response_type":'code',
                    "client_id":self._client_id,
                    "redirect_uri":self._redirect_uri,
                    "state":self._client_state,
                    "scope":self._auth_scopes}

        return parameters

    @property
    def _second_request_access_refresh_token_params(self):
        payload = {"grant_type":'authorization_code',
                   "code": self._auth_code,
                    "redirect_uri":self._redirect_uri,}

        headers = {"Authorization":f'Basic {self.build_authorization_string}',
                    "Content-Type":'application/x-www-form-urlencoded'}

        return [payload, headers]

    @property
    def _third_request_refreshed_access_token_params(self):
        payload = {"grant_type":'refresh_token',
                   "refresh_token": self._refresh_token}

        headers = {"Authorization":f'Basic {self.build_authorization_string}',
                    "Content-Type":'application/x-www-form-urlencoded'}

        return [payload, headers]

    @property
    async def _token_valid(self):
        if time.time() >= self._expired:
            return False
        else:
            return True

    async def _first_request_authorization(self):

        webbrowser.open('https://accounts.spotify.com/authorize?' + urlencode(self._first_request_auth_params), new=1)

        asyncio.create_task(asyncio.to_thread(self._start_local_http_server))

        wait_timer=0
        while self._local_http_server_wait > wait_timer:
            if self._auth_code:
                self.logger.debug("capturing authentication code")

                # Captruing has been disabled in this release
                # set_key(BRUTE_ENV, "_auth_code", self._auth_code)
                break
            if wait_timer == self._local_http_server_wait:
                try:
                    requests.get(self._redirect_uri, params="terminate server")
                except requests.exceptions.ConnectionError as e:
                    self.logger.debug("The local server failed to recieve a redirect request within the alloted time the program will now exit")
                    exit()

            wait_timer+=1
            self.logger.debug(f"Waiting for redirect...")
            await asyncio.sleep(1.5)

    async def _second_request_access_token(self):
        with requests.session() as s:
            test = s.post('https://accounts.spotify.com/api/token',
                         headers=self._second_request_access_refresh_token_params[1],
                         data=self._second_request_access_refresh_token_params[0])

        api_response = json.loads(test.content.decode())

        if test.status_code == 200:

            self._refresh_token = api_response["refresh_token"]
            self._access_token = api_response["access_token"]
            self._expires_in = api_response["expires_in"]
            self._expired = time.time() + (api_response["expires_in"] - 5)
            self._scope = api_response["scope"]

            await self._write_values_to_env()

        else:
            self.logger.debug("Request Access Token Failed")
            self.logger.debug(api_response)

    async def _third_request_refreshed_access_token(self):
        with requests.session() as s:
            resp = s.post('https://accounts.spotify.com/api/token',
                          headers=self._third_request_refreshed_access_token_params[1],
                          data=self._third_request_refreshed_access_token_params[0])

            api_response = json.loads(resp.content.decode())

        if resp.status_code == 200:
            self.logger.debug(f"HTTP_status:{resp.status_code} url:{resp.url} --> TOKEN REFRESHED")

            self._access_token = api_response["access_token"]
            self._token_type = api_response["token_type"]
            self._expires_in = api_response["expires_in"]
            self._expired = time.time() + (api_response["expires_in"] - 5)
            self._scope = api_response["scope"]
            self.authenticated = True

            await self._write_values_to_env()

        else:
            self.logger.debug("TOKEN REFRESHED FAILED")
            self.logger.debug(api_response)

    def _start_local_http_server(self, event: asyncio.Event=None):
        self.logger.debug(f"If no response is recieved the server will cose and script will exit")
        self.logger.debug(f"Thread started for local HTTP server at {time.strftime('%X')}")
        self.logger.debug(f"Starting local http server at {time.strftime('%X')}")
        try:
            self._local_http_server.handle_request() #<-- Blocking
            _redirect_completed = True
        except Exception as e:
            self.logger.debug(e)
            self.logger.debug(f"thread stopping for local http server at {time.strftime('%X')}")
            exit()

        if not _redirect_completed == "/?terminate%20server":
            self._auth_code = Custom_RequestHandler.get_result.split("=")[1].replace("&state", "")

    async  def _write_values_to_env(self, test_value=None):

        if self._enable_env_write:
            set_key(BRUTE_ENV, "_refresh_token", self._refresh_token)
            set_key(BRUTE_ENV, "_scopes", self._scope)
            set_key(BRUTE_ENV, "_expired_at", str(self._expired))

            # Currently Not Capturing
            # set_key(BRUTE_ENV, "_auth_code", self._auth_code)
            # set_key(BRUTE_ENV, "_access_token", self._access_token)

async def auth_flow() -> None:
    spotify_auth = OauthSpotify_Authorization_Code_Flow(local_test=True, scopes=["test"])

    # if not await spotify_auth._auth_cache_available:
    #     await spotify_auth._first_request_authorization()
    #     await spotify_auth._second_request_access_token()
    #     await spotify_auth._third_request_refreshed_access_token()

if __name__ == '__main__':
    asyncio.run(auth_flow())
