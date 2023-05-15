from config import get_server_data, RADIUS, WIDTH_ROOM, HEIGHT_ROOM

import socket
import threading
import pygame
from pickle import dumps, loads
from Game_package import Player


def get_ready_socket_with_name() -> tuple[socket.socket | None, str]:
    server_ip, port = get_server_data()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        sock.connect((server_ip, port))
    except (Exception,):
        print("Server connection failed")
        print("Trying to connect to a local server")
        try:
            sock.connect(('localhost', 10000))
        except (Exception,):
            print("Trying to connect to a local server failed")
            return None, ""

    name = loads(sock.recv(1024))

    if loads(sock.recv(64)) != '!':
        print("No acknowledgement signal received")
        sock.close()
        exit()

    # confirm connection
    sock.send(dumps({"!": True}))

    return sock, name


class Grid:
    def __init__(self, screen: pygame.Surface, width, height):
        self.screen = screen
        self.x = width
        self.y = height
        self.start_size = 200
        self.size = self.start_size

    def update(self, r_x, r_y):
        self.x = -self.size + (-r_x) % self.size
        self.y = -self.size + (-r_y) % self.size

    def draw(self, background: pygame.image):
        self.screen.blit(background, (0, 0))

    def fill(self, color: tuple[int, int, int]):
        self.screen.fill(color)

    def show_messages(self, talk):
        for num_phrase, phrase in enumerate(talk):
            black = (0, 0, 0)
            white = (255, 255, 255)
            font_obj = pygame.font.Font('freesansbold.ttf', 20)
            text_surface_obj = font_obj.render(phrase, True, black, white)

            self.screen.blit(text_surface_obj, (WIDTH_ROOM + 40, num_phrase * 20))


def draw_players(screen, players, colour: tuple[int, int, int]):
    def write_name(x, y, r, name):
        nonlocal screen
        font = pygame.font.Font(None, r)
        text = font.render(name, True, (0, 0, 0))
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)

    for player in players:
        pygame.draw.circle(screen, colour, (player.x, player.y), RADIUS)
        write_name(player.x, player.y, RADIUS, player.name)


def main():
    running = True
    talk: list[str] = []
    message: str = ""
    unsent_message: str = ""
    my_socket, my_name = get_ready_socket_with_name()
    if not my_socket:
        return 0
    width_window, height_window = WIDTH_ROOM + 400, HEIGHT_ROOM
    colour = (255, 255, 100)
    background = pygame.image.load("Game_package/background.png")
    missing_table = -1

    table_number: int = missing_table
    desired_table_number: int = 0

    pygame.init()
    screen = pygame.display.set_mode((width_window, height_window))
    pygame.display.set_caption('Cocktail party')
    grid = Grid(screen, width_window, height_window)

    def input_from_console():
        nonlocal talk, message, unsent_message
        while running:
            message = input()
            if message and table_number == desired_table_number and message_forming:
                unsent_message = message

    threading.Thread(target=input_from_console).start()

    message_forming = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                for i, event_key in enumerate([pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]):
                    if event.key == event_key:
                        desired_table_number = i
                        break

        message_to_server = {"unsent_message": "",
                             "desired_table_number": desired_table_number}
        if message_forming:
            message_to_server["unsent_message"] = unsent_message
        unsent_message = ""

        if table_number != desired_table_number:
            message_forming = False
            table_number = missing_table
        my_socket.sendall(dumps(message_to_server))
        message_to_server["unsent_message"] = ""
        # getting new game state
        try:
            players: list[Player] = loads(my_socket.recv(2 ** 20))
        except (Exception,):
            running = False
            continue
        silver = (192, 192, 192)
        grid.fill(silver)
        grid.draw(background)
        draw_players(screen, players, colour)
        for player in players:
            if player.table_number == table_number and table_number > 0 and player.unsent_message:
                talk.append(f"{player.name}: {player.unsent_message}")
        grid.show_messages(talk[-30:])

        for player in players:
            if player.name == my_name:
                table_number = player.table_number
        if table_number == desired_table_number and table_number > 0:
            if not message_forming:
                message_forming = True
                print(f"You come to table {table_number} and you can talk")
        else:
            message_forming = False

        pygame.display.update()

    pygame.quit()
    print("Type something into the console and it will close")


if __name__ == "__main__":
    main()
