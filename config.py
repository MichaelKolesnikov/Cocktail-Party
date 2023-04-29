from os import getenv
from dotenv import load_dotenv

load_dotenv()
RADIUS = 30
FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 700, 700
BOTS_QUANTITY = 2


def get_server_data() -> tuple[str, int]:
    server_ip = str(getenv("SERVER_IP"))
    print(server_ip)
    port = 10000 if server_ip in ('127.0.0.1', 'localhost') else 2000

    return server_ip, port
