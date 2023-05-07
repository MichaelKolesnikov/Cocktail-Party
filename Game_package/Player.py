class Player:
    def __init__(self, conn, addr_, x: int, y: int, name: str):
        self.conn = conn
        self.addr = addr_
        self.x = x
        self.y = y
        self.table_number = -1
        self.desired_table_number = 0
        self.name = name
        self.unsent_message = ""
        self.errors = 0
        self.dead = 0
        self.ready = False
        self.abs_speed = 5
        self.speed_x = 0
        self.speed_y = 0

    def set_options(self, data_):
        data_ = data_[1:-1].split(' ')
        self.name = data_[0]

    def change_speed(self, v):
        if (v[0] == 0) and (v[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            len_v = (v[0] ** 2 + v[1] ** 2) ** 0.5
            v = (v[0] / len_v, v[1] / len_v)
            v = (v[0] * self.abs_speed, v[1] * self.abs_speed)
            self.speed_x, self.speed_y = v[0], v[1]

    def pickle_able_copy(self):
        pickle_able_player = Player(None, None, self.x, self.y, self.name)
        pickle_able_player.table_number = self.table_number
        pickle_able_player.desired_table_number = self.desired_table_number
        pickle_able_player.unsent_message = self.unsent_message
        pickle_able_player.errors = self.errors
        pickle_able_player.dead = self.dead
        pickle_able_player.ready = self.ready
        pickle_able_player.abs_speed = self.abs_speed
        pickle_able_player.speed_x = self.speed_x
        pickle_able_player.speed_y = self.speed_y
        return pickle_able_player


class Bot(Player):
    count_gamers = 6

    def __init__(self, conn, addr_, x: int, y: int, name: str):
        super().__init__(conn, addr_, x, y, name)
        self.opinions_about_players = [0.8 for _ in range(self.count_gamers)]
        self.game_state = [-1 for _ in range(self.count_gamers)]

    def send_command(self):
        ind = 0
        max_opinion = 0
        for i in range(self.count_gamers):
            if self.game_state[i] != -1 and self.game_state[i] != 0 and max_opinion < self.opinions_about_players[i]:
                ind = i
                max_opinion = self.opinions_about_players[i]
        if max_opinion < 0.2:
            table_number = 0
        else:
            table_number = self.game_state[ind]
        message = '<' + str(table_number) + '>'
        return message


    def update_opinions(self):
        pass

    def get_game_state(self, game_state):
        if len(game_state) < self.count_gamers:
            game_state += [0] * (self.count_gamers - len(game_state))
        elif len(game_state) > self.count_gamers:
            game_state = game_state[:self.count_gamers]
        self.game_state = game_state
