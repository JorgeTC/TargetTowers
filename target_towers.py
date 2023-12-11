from queue import Queue
from itertools import product
from typing import Iterator


class MoveException(Exception):
    ...


class Column:
    HEIGHT = 4

    def __init__(self, values: 'list[int | None]'):
        self.positions = [values[i] if i < len(values) else None
                          for i in range(self.HEIGHT)]
        try:
            self.index = self.positions.index(None)
        except ValueError:
            self.index = self.HEIGHT

    def get(self):
        if self.index == 0:
            raise MoveException
        value = self.positions[self.index - 1]
        self.positions[self.index - 1] = None
        self.index -= 1
        return value

    def put(self, item: int):
        if self.index == self.HEIGHT:
            raise MoveException
        self.positions[self.index] = item
        self.index += 1

    def __eq__(self, other: 'Column'):
        return all(self.positions[i] == other.positions[i]
                   for i in range(Column.HEIGHT))

    def __hash__(self):
        return hash(tuple(self.positions))


class State:
    COLUMNS = 3

    def __init__(self, columns: 'list[list[int]]'):
        all_columns = (Column(columns[i]) for i in range(self.COLUMNS))
        self.columns = tuple(all_columns)

    def move(self, ori: int, dest: int):
        dest_column = self.columns[dest]
        ori_column = self.columns[ori]
        taken_element = ori_column.get()
        dest_column.put(taken_element)

    def copy(self):
        return State([column.positions for column in self.columns])

    def __eq__(self, other: 'State'):
        return all(self.columns[i] == other.columns[i] for i in range(State.COLUMNS))

    def __hash__(self):
        return hash(self.columns)

    @staticmethod
    def _format_number(number: int | None) -> str:
        return '_' if number is None else str(number)

    def __str__(self):
        return '\n'.join(' '.join(self._format_number(column.positions[i])
                                  for column in self.columns)
                         for i in reversed(range(Column.HEIGHT)))


def iter_states(current_state: State) -> 'Iterator[State]':
    for ori_index, dest_index in product(range(current_state.COLUMNS), repeat=2):
        if ori_index == dest_index:
            continue
        new_state = current_state.copy()
        try:
            new_state.move(ori_index, dest_index)
        except MoveException:
            continue
        yield new_state


def create_path(travel_map: 'dict[State, State | None]', ori_state: State, dest_state: State):
    full_path = [dest_state]
    current_state = dest_state
    while current_state != ori_state:
        current_state = travel_map[current_state]
        full_path.append(current_state)
    full_path.reverse()
    return full_path


def find_solution(ori_state: State, dest_state: State):
    travel_map: dict[State, State | None] = {ori_state: None}
    to_visit: Queue[State] = Queue()
    to_visit.put(ori_state)

    while True:
        if to_visit.empty():
            break
        current_state = to_visit.get()

        for new_state in iter_states(current_state):
            if new_state in travel_map:
                continue
            travel_map[new_state] = current_state
            if new_state == dest_state:
                return create_path(travel_map, ori_state, dest_state)
            to_visit.put(new_state)

    raise ValueError(f"Impossible to get from:"
                     f"\n{ori_state} \nto:\n{dest_state}")


def main():
    ori_state = State([[1, 2, None, None],
                       [3, 4, 9, None],
                       [5, 6, 7, 8]])

    dest_state = State([[5, 6, None, None],
                        [4, 3, 9, None],
                        [2, 7, 1, 8]])

    solution = find_solution(ori_state, dest_state)

    for state in solution:
        print(state)
        print()


if __name__ == '__main__':
    main()
