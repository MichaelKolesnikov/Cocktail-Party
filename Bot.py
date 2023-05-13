from config import get_server_data

import socket
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


def main():
    running = True
    talk: list[str] = []
    message: str = ""
    unsent_message: str = ""
    my_socket, my_name = get_ready_socket_with_name()
    if not my_socket:
        return 0
    missing_table = -1

    table_number: int = missing_table
    desired_table_number: int = 0

    message_forming = False
    while running:
        # получение сообщения от бота о переходе к новому столу
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        #     elif event.type == pygame.KEYDOWN:
        #         for i, event_key in enumerate([pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]):
        #             if event.key == event_key:
        #                 desired_table_number = i
        #                 break

        message_to_server = {"unsent_message": "",
                             "desired_table_number": desired_table_number}
        if message_forming:
            message_to_server["unsent_message"] = unsent_message
        unsent_message = ""

        if table_number != desired_table_number:
            message_forming = False
            table_number = missing_table
        my_socket.send(dumps(message_to_server))
        message_to_server["unsent_message"] = ""
        # getting new game state
        try:
            players: list[Player] = loads(my_socket.recv(2 ** 20))
        except (Exception,):
            running = False
            continue
        for player in players:
            if player.table_number == table_number and table_number > 0 and player.unsent_message:
                talk.append(f"{player.name}: {player.unsent_message}")

        for player in players:
            if player.name == my_name:
                table_number = player.table_number
        if table_number == desired_table_number and table_number > 0:
            if not message_forming:
                message_forming = True
        else:
            message_forming = False


if __name__ == "__main__":
    main()
