from config import *

import socket
import time
from random import randint
from pickle import loads, dumps

from Game_package import Table, Place
from Game_package import get_not_taken_name, free_name
from Game_package import Player, Bot


tables = [
        Table([Place(650, 86), Place(650, 186), Place(650, 286), Place(650, 386), Place(650, 486), Place(650, 586)],
              6, 0),
        Table([Place(162, 135), Place(109, 224), Place(215, 224)], 3, 1),
        Table([Place(439, 135), Place(385, 224), Place(492, 224)], 3, 2),
        Table([Place(162, 485), Place(109, 574), Place(215, 574)], 3, 3),
        Table([Place(439, 485), Place(385, 574), Place(492, 574)], 3, 4)]


def get_ready_socket() -> socket.socket | None:
    server_ip, port = get_server_data()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        sock.bind((server_ip, port))
    except (Exception,):
        print("An attempt to work on a remote server failed")
        print("Trying to work over a local network")
        try:
            sock.bind(('localhost', 10000))
        except (Exception,):
            print("Trying to work over a local network failed")
            return None

    sock.setblocking(False)
    sock.listen(6)

    return sock


def update(player_: Player):
    if player_.table_number != player_.desired_table_number:
        if player_.table_number != -1:
            tables[player_.table_number].remove_visitor(player_.name)
        player_.table_number = -1
        empty_table_place = tables[player_.desired_table_number].get_empty_place()
        d_x, d_y = empty_table_place.x - player_.x, empty_table_place.y - player_.y
        player_.change_speed((d_x, d_y))

        if abs(d_x) < RADIUS and abs(d_y) < RADIUS:
            player_.table_number = player_.desired_table_number
            tables[player_.table_number].add_visitor(player_.name)
            player_.change_speed((0, 0))

    if player_.x - RADIUS <= 0:
        if player_.speed_x >= 0:
            player_.x += player_.speed_x
    else:
        if player_.x + RADIUS >= WIDTH_ROOM:
            if player_.speed_x <= 0:
                player_.x += player_.speed_x
        else:
            player_.x += player_.speed_x

    if player_.y - RADIUS <= 0:
        if player_.speed_y >= 0:
            player_.y += player_.speed_y
    else:
        if player_.y + RADIUS >= HEIGHT_ROOM:
            if player_.speed_y <= 0:
                player_.y += player_.speed_y
        else:
            player_.y += player_.speed_y
    player_.x = int(player_.x)
    player_.y = int(player_.y)


def find(s):
    opened = None
    for i in range(len(s)):
        if s[i] == '<':
            opened = i
        if s[i] == '>' and opened is not None:
            closed = i
            res = s[opened + 1:closed]
            res = list(map(int, res.split(',')))
            return res
    return ''


def main():
    ready_socket = get_ready_socket()

    players: list[Player | Bot] = []

    tick = -1
    server_works = True
    while server_works:
        tick += 1
        time.sleep(1 / FPS)
        # bringing in new players
        if tick == 200:
            tick = 0
            try:
                new_socket, addr = ready_socket.accept()
                print(f'Connected {addr}')
                new_socket.setblocking(False)

                new_player = Player(new_socket, addr,
                                    randint(0, WIDTH_ROOM),
                                    randint(0, HEIGHT_ROOM),
                                    get_not_taken_name())
                new_socket.send(dumps(new_player.name))
                new_socket.send(dumps('!'))
                players.append(new_player)
            except (Exception,):
                pass
        # receiving messages from all players
        for player in players:
            if type(player) == Player:
                try:
                    data: dict = loads(player.conn.recv(1024))
                    if "!" in data:  # confirm connection
                        player.ready = True
                    else:  # getting desired table number and new phrase
                        if data.get("desired_table_number") != player.desired_table_number:
                            desired_table_number = data.get("desired_table_number")
                            if tables[desired_table_number].are_empty_places():
                                player.desired_table_number = desired_table_number
                        if data.get("unsent_message"):
                            unsent_message = data.get("unsent_message")
                            player.unsent_message = unsent_message
                except (Exception,):
                    pass
            elif type(player) == Bot:
                desired_table_number = find(player.send_command())[0]
                if tables[desired_table_number].are_empty_places():
                    player.desired_table_number = desired_table_number
            update(player)

        # sending new game state
        pickle_able_players = [player.pickle_able_copy() for player in players]
        for player in players:
            player.unsent_message = ""
        for i in range(len(players)):
            if type(players[i]) == Player and players[i].ready:
                try:
                    players[i].conn.send(dumps(pickle_able_players))
                    players[i].errors = 0
                except (Exception,):
                    players[i].errors += 1
            elif type(players[i]) == Bot:
                players[i].get_game_state([player.table_number for player in players])

        # clearing the list of disconnected clients
        for player in players:
            if RADIUS == 0:
                if player.conn is not None:
                    player.dead += 1
                else:
                    player.dead += 300

            if (player.errors == 500) or (player.dead == 300):
                if player.conn is not None:
                    player.conn.close()
                tables[player.table_number].remove_visitor(player.name)
                players.remove(player)
                free_name(player.name)
    ready_socket.close()


if __name__ == "__main__":
    main()
