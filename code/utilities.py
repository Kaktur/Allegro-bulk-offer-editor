import json

global paths,path_mod,session,setting_file
session = 0
paths = {
"settings_file": "data//settings.json",
"Allegro_token": "data//Allegro_connections.json",
"Allegro_token_sandbox": "data//Allegro_connections_sandbox.json",
}

setting_file = None
def get_setting(setting):
    """
    Used to get specific settings from the setting file. Pass "setting" as a string containing name of setting.
    """
    global setting_file
    if setting_file == None: 
        with open(paths["settings_file"], mode='r') as file:
            setting_file = json.load(file)
    return setting_file[setting]


from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import time
import requests

class Allegro:

    global sandbox,DEFAULT_OAUTH_URL,DEFAULT_API_URL
    sandbox = True

    DEFAULT_API_URL = 'https://api.allegro.pl'
    DEFAULT_REDIRECT_URI = 'http://localhost:8000'
    DEFAULT_OAUTH_URL = 'https://allegro.pl/auth/oauth'

    def set_sandbox(sbox = None):
        """
        Setter function for changing if wrapper operates on the sand_box environment or real. 
        Pass bool to change environment, true - sand_box, false - real, none - toggle
        """
        global DEFAULT_OAUTH_URL,DEFAULT_API_URL,sandbox
        if sbox == None:
            sandbox = not sandbox
        else:
            sandbox = sbox
        if sandbox:
            DEFAULT_OAUTH_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth"
            DEFAULT_API_URL = "https://api.allegro.pl.allegrosandbox.pl"
        return f"sandbox is {sandbox}"


    # Implementujemy funkcję, której parametry przyjmują kolejno:
    #  - client_id (ClientID), api_key (API Key) oraz opcjonalnie redirect_uri i oauth_url
    # (jeżeli ich nie podamy, zostaną użyte domyślne zdefiniowane wyżej)
    def get_access_code(client_id, api_key, redirect_uri=DEFAULT_REDIRECT_URI, oauth_url=None):
        """
        Creates access token to Allegro API, utility function for create_token()
        """
        global DEFAULT_OAUTH_URL
        if oauth_url == None:
            oauth_url=DEFAULT_OAUTH_URL
        # zmienna auth_url zawierać będzie zbudowany na podstawie podanych parametrów URL do zdobycia kodu
        auth_url = '{}/authorize' \
                   '?response_type=code' \
                   '&client_id={}' \
                   '&api-key={}' \
                   '&redirect_uri={}'.format(oauth_url, client_id, api_key, redirect_uri)
    
        # uzywamy narzędzia z modułu requests - urlparse - służy do spardowania podanego url 
        # (oddzieli hostname od portu)
        parsed_redirect_uri = requests.utils.urlparse(redirect_uri)

        # definiujemy nasz serwer - który obsłuży odpowiedź allegro (redirect_uri)
        server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port

        # Ta klasa pomoże obsłużyć zdarzenie GET na naszym lokalnym serwerze
        # - odbierze żądanie (odpowiedź) z serwisu allegro
        class AllegroAuthHandler(BaseHTTPRequestHandler):
            def __init__(self, request, address, server):
                super().__init__(request, address, server)

            def do_GET(self):
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                self.server.path = self.path
                self.server.access_code = self.path.rsplit('?code=', 1)[-1]

        # Wyświetli nam adres uruchomionego lokalnego serwera
        print('server_address:', server_address)

        # Uruchamiamy przeglądarkę, przechodząc na adres zdefiniowany do uzyskania kodu dostępu
        # wyświetlić się powinien formularz logowania do serwisu Allegro.pl
        webbrowser.open(auth_url)

        # Uruchamiamy nasz lokalny web server na maszynie na której uruchomiony zostanie skrypt
        # taki serwer dostępny będzie pod adresem http://localhost:8000 (server_address)
        httpd = HTTPServer(server_address, AllegroAuthHandler)
        print('Waiting for response with access_code from Allegro.pl (user authorization in progress)...')

        # Oczekujemy tylko jednego żądania
        httpd.handle_request()

        # Po jego otrzymaniu zamykamy nasz serwer (nie obsługujemy już żadnych żądań)
        httpd.server_close()

        # Klasa HTTPServer przechowuje teraz nasz access_code - wyciągamy go
        _access_code = httpd.access_code

        # Dla jasności co się dzieje - wyświetlamy go na ekranie
        print('Got an authorize code: ', _access_code)

        # i zwracamy jako rezultat działania naszej funkcji
        return _access_code
    
    def sign_in(client_id, client_secret, access_code, api_key, redirect_uri=DEFAULT_REDIRECT_URI, oauth_url=None):
        """
        Signs in to a user API account connected to Allegro account.
        """
        global DEFAULT_OAUTH_URL
        if oauth_url == None:
            oauth_url=DEFAULT_OAUTH_URL
        
        token_url = oauth_url + '/token'

        access_token_data = {'grant_type': 'authorization_code',
                             'code': access_code,
                             'api-key': api_key,
                             'redirect_uri': redirect_uri}

        response = requests.post(url=token_url,
                                 auth=requests.auth.HTTPBasicAuth(client_id, client_secret),
                                 data=access_token_data)

        return response.json()
    
    def refresh_token(client_id, client_secret, refresh_token, api_key, redirect_uri=DEFAULT_REDIRECT_URI, oauth_url=None):
        """
        Refreshes a expired ticket with saved data from token creation.
        """
        global DEFAULT_OAUTH_URL
        if oauth_url == None:
            oauth_url=DEFAULT_OAUTH_URL


        token_url = oauth_url + '/token'

        access_token_data = {'grant_type': 'refresh_token',
                             'api-key':  api_key,
                             'refresh_token': refresh_token,
                             'redirect_uri': redirect_uri}

        response = requests.post(url=token_url,
                                 auth=requests.auth.HTTPBasicAuth(client_id, client_secret),
                                 data=access_token_data)

        return response.json()
    
    
    def create_token():
        """
        Creates and stores access token. Will open browser window. 
        Tokens are stored in "Allegro_connections_sandbox.json" and "Allegro_connections.json" respectively
        """
        if sandbox:
            client_id = get_setting("Allegro_Sandbox_Id")
            client_secret = get_setting("Allegro_Sandbox_Secret")
        else:
            client_id = get_setting("Allegro_Id")
            client_secret = get_setting("Allegro_Secret")
        
        api_key = client_secret
        access_code = Allegro.get_access_code(client_id, api_key)
        response = Allegro.sign_in(client_id, client_secret, access_code, api_key)

        expiration = response["expires_in"]
        print(f"Will expire in: {expiration}")

        #modify "expires in" to be a time stamp
        response["expires_in"] = time.time() + expiration

        a_token = paths["Allegro_token"]
        if sandbox:
            a_token = paths["Allegro_token_sandbox"]
        with open(a_token, mode='w') as file:
           json.dump(response, file, indent = 4)
        
    def check_token():
        """
        Checks if token has expired and if so refreshes it
        """
        a_token = paths["Allegro_token"]
        if sandbox:
            a_token = paths["Allegro_token_sandbox"]
        with open(a_token, mode='r') as file:
           data = json.load(file)
        expired = False
        #check if expired
        if time.time() >= data["expires_in"]:
            expired = True
        if expired:
            if sandbox:
                client_id = get_setting("Allegro_Sandbox_Id")
                client_secret = get_setting("Allegro_Sandbox_Secret")
            else:
                client_id = get_setting("Allegro_Id")
                client_secret = get_setting("Allegro_Secret")
            api_key = client_secret
            refresh_token = data["refresh_token"]
            response = Allegro.refresh_token(client_id,client_secret,refresh_token,api_key)
            if "error" in response.keys() :
                print(response)
            else:
                a_token = paths["Allegro_token"]
                if sandbox:
                    a_token = paths["Allegro_token_sandbox"]
                with open(a_token, mode='w') as file:
                    json.dump(response, file, indent = 4)
                return response
        else:
            return data
    
    from typing import Literal
    def send(type: Literal["GET",'POST', 'PUT', 'PATCH', 'DELETE'], path: str, params: dict = None, dump: bool = False):
        """
        Allows for sending any Allegro API request, specify type of action and a request path plus necessary data depending on type of action.
        Returns result or in case of a error prints error and returns "Error"
        """
        #args = None, method = None , json = None
        data = Allegro.check_token()

        headers = {}
        headers['charset'] = 'utf-8'
        headers['Accept-Language'] = 'pl-PL'
        headers['Content-Type'] = 'application/vnd.allegro.public.v1+json'
        #'application/json'
        # headers['Api-Key'] = data.api_key
        headers['Accept'] = 'application/vnd.allegro.public.v1+json'
        headers['Authorization'] = "Bearer {}".format(data['access_token'])

        # Inicjujemy naszą sesję (przechowuje nagłówki itd.)
        # konstrukcja with pozwala na użycie sesji tylko w jej obrębie
        # kiedy wyczerpią się instrukcje wewnątrz niej
        # straci ona ważność (zostanie zamknięta)
        global DEFAULT_API_URL
        with requests.Session() as session:
            session.headers.update(headers)
            url = DEFAULT_API_URL + path
            if type == 'GET':
                #Wykorzystywana do pobierania danych. Wszystkie metody GET mogą być wołane wielokrotnie, gdyż nie modyfikują żadnych zasobów Allegro.
                response = session.get(url,  params = params)
            elif type == 'POST':
                #Wykorzystywana do utworzenia nowego zasobu (np. utworzenie nowego draftu oferty tworzy zasób typu /sale/offers. Dwukrotne wywołanie metody POST na zasobie /sale/offers spowoduje stworzenie dwóch draftów ofert na Allegro.
                 response = session.post(url, params = params)
                 #method ,json , args
            elif type == 'PUT':
                #Wykorzystywana do edycji zasobu (np. edycja opisu wystawionej na Allegro oferty). Dwukrotne wywołanie metody PUT na tym samym zasobie jest bezpieczne.
                response = session.put(url, json = params)
                #method, args
            elif type == 'PATCH':
                #Wykorzystywana do częściowej edycji zasobu (np. edycja ceny, bez konieczności przesyłania całego modelu oferty).
                response = session.patch(url, json = params)
                #method, args
            elif type == 'DELETE':
                #Wykorzystywana do usuwania zasobów.
                response = session.delete(url, params = params)
            
            response = response.json()
            if 'errors' in response.keys():
                print(response)
                response = "Error"
            elif dump:
                print(response)
            return response
        

        