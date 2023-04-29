class Place:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Table:
    def __init__(self, places: list, max_count_visitors: int, number: int):
        self.places = places
        self.place_taken_by = [''] * len(self.places)
        self.visitors = []
        self.max_count_visitors = max_count_visitors
        self.number = number

    def get_empty_place(self) -> Place:
        for i in range(len(self.places)):
            if not self.place_taken_by[i]:
                return self.places[i]

    def are_empty_places(self) -> bool:
        return len(self.visitors) < self.max_count_visitors

    def add_visitor(self, name_new_visitor: str):
        for i in range(len(self.places)):
            if not self.place_taken_by[i]:
                self.visitors.append(name_new_visitor)
                self.place_taken_by[i] = name_new_visitor
                break

    def remove_visitor(self, name_visitor: str):
        for i in range(len(self.places)):
            if self.place_taken_by[i] == name_visitor:
                self.visitors.remove(name_visitor)
                self.place_taken_by[i] = ''
                break
