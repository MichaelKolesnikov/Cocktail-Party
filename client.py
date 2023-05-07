import threading

from config import get_server_data, RADIUS, WIDTH_ROOM, HEIGHT_ROOM

import socket
import pygame
from pickle import dumps, loads


def find(s) -> str:
    opened = None
    for ind in range(len(s)):
        if s[ind] == '<':
            opened = ind
        if s[ind] == '>' and opened is not None:
            closed = ind
            res = s[opened + 1:closed]
            return res
    return ''


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

    name = sock.recv(1024).decode()

    if sock.recv(64).decode() != '!':
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
        for num_phrase, phrase in enumerate(talk[-10:]):
            black = (0, 0, 0)
            white = (255, 255, 255)
            font_obj = pygame.font.Font('freesansbold.ttf', 20)
            text_surface_obj = font_obj.render(phrase, True, black, white)

            self.screen.blit(text_surface_obj, (WIDTH_ROOM + 40, num_phrase * 20))


def write_name(screen, x, y, r, name):
    font = pygame.font.Font(None, r)
    text = font.render(name, True, (0, 0, 0))
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)


def draw_players(screen, data_, colour: tuple[int, int, int]):
    for ind in range(len(data_)):
        j = data_[ind].split(' ')

        x = int(j[0])
        y = int(j[1])
        pygame.draw.circle(screen, colour, (x, y), RADIUS)

        if len(j) == 3:
            write_name(screen, x, y, RADIUS, j[2])


def main():
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
        while True:
            message = input()
            if message and table_number == desired_table_number and message_forming:
                talk.append(message)
                unsent_message = message

    threading.Thread(target=input_from_console).start()

    message_forming = False
    running = True
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
        if unsent_message and message_forming:
            message_to_server["unsent_message"] = unsent_message
            unsent_message = ""

        if table_number != desired_table_number:
            message_forming = False
            table_number = missing_table
        my_socket.send(dumps(message_to_server))
        message_to_server["unsent_message"] = ""

        # getting new game state
        try:
            data = loads(my_socket.recv(2 ** 15))
        except (Exception,):
            running = False
            continue
        data = find(data)
        data = data.split(',')
        if data != ['']:
            silver = (192, 192, 192)
            grid.fill(silver)
            grid.draw(background)
            draw_players(screen, data[:-1], colour)
            grid.show_messages(talk)

            table_number = int(data[-1])
            if table_number == desired_table_number and table_number != 0:
                if not message_forming:
                    message_forming = True
                    print(f"You come to table {table_number} and you can talk")
            else:
                message_forming = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
