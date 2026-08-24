from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

api_link = "https://api.gametools.network/bf1/stats/?name={player_id}&platform=pc"
user_input = input("Enter the player ID: ")
api_link = api_link.format(player_id=user_input)

request = Request(api_link, headers={"User-Agent": "BF1Bot/1.0"})

try:
    with urlopen(request) as response:
        if response.status == 200:
            data = response.read().decode("utf-8")
            print(data)
except (HTTPError, URLError) as error:
    print(f"Request failed: {error}")
    