from queue import Queue
from itertools import product
from typing import Iterator


class MoveException(Exception):
    '''
    Exception to throw in the class Column when
    get is called on an empty column or put is called in a full column
    '''
    ...


class Column:
    # Set the maximum elements a Column can hold
    HEIGHT = 4

    def __init__(self, values: 'list[int | None]'):
        # A list of `HEIGHT` elements with the elements in the column positions
        self.positions = [values[i] if i < len(values) else None
                          for i in range(self.HEIGHT)]

        # Index to the first empty cell in the column
        try:
            self.index = self.positions.index(None)
        except ValueError:
            # If there is no None in the tower, it is full
            self.index = self.HEIGHT

    def get(self):
        '''
        Removes from the tower its top element.
        `MoveException` is raised if the column is empty
        '''

        # If the column is empty cannot get any element from it
        if self.index == 0:
            raise MoveException

        # Get the top element of the column
        value = self.positions[self.index - 1]
        # Set that position to empty
        self.positions[self.index - 1] = None
        # Decrease the index
        self.index -= 1
        # Return the top element
        return value

    def put(self, item: int):
        '''
        Drops on the tower a new element.
        `MoveException` is raised if the column is full
        '''

        # If the column is full cannot accept any more elements
        if self.index == self.HEIGHT:
            raise MoveException

        self.positions[self.index] = item
        self.index += 1

    def __eq__(self, other: 'Column'):
        '''
        Two columns are considered equal when their positions lists are identical
        '''
        return all(self.positions[i] == other.positions[i]
                   for i in range(Column.HEIGHT))

    def __hash__(self):
        '''
        Because __eq__ has been overridden we must define a proper __hash__ function
        '''
        return hash(tuple(self.positions))


class State:
    # Set the amount of Columns I have
    COLUMNS = 3

    def __init__(self, columns: 'list[list[int]]'):
        # Store the input lists as a tuple of Columns.
        # Stored in a tuple as the amount will be constant.
        # There will never be more columns than expected.
        all_columns = (Column(columns[i]) for i in range(self.COLUMNS))
        self.columns = tuple(all_columns)

    def move(self, ori: int, dest: int):
        '''
        Gets the index of two columns to move its top element.
        If the origin one is empty or the destination one is empty, `MoveException` is raised.
        '''

        # Select the two columns
        dest_column = self.columns[dest]
        ori_column = self.columns[ori]

        # Take the top element from the origin column
        taken_element = ori_column.get()
        # Drop the element over the destination column
        dest_column.put(taken_element)

    def copy(self):
        return State([column.positions for column in self.columns])

    def __eq__(self, other: 'State'):
        '''
        Two states are equal when all their columns are equal
        '''
        return all(self.columns[i] == other.columns[i] for i in range(State.COLUMNS))

    def __hash__(self):
        '''
        Because __eq__ has been overridden we must define a proper __hash__ function
        '''
        return hash(self.columns)

    @staticmethod
    def _format_number(number: int | None) -> str:
        return '_' if number is None else str(number)

    def __str__(self):
        '''
        Method to allow pretty print for this class.
        Empty cells will be represented as _.
        '''
        return '\n'.join(' '.join(self._format_number(column.positions[i])
                                  for column in self.columns)
                         for i in reversed(range(Column.HEIGHT)))


def iter_states(current_state: State) -> 'Iterator[State]':
    '''
    Iterates all the possible states accessible from the input State
    '''

    # I will get a new state for each possible move.
    # Iterate every pair of indices for columns to perform the move
    for ori_index, dest_index in product(range(current_state.COLUMNS), repeat=2):
        # If the indices are equal, the movement cannot be performed
        if ori_index == dest_index:
            continue

        # Create a copy of the current state to perform the movement on
        new_state = current_state.copy()
        try:
            new_state.move(ori_index, dest_index)
        except MoveException:
            # Cannot perform a movement for the selected indices
            continue

        # I performed a movement, I got a new State
        yield new_state


def create_path(travel_map: 'dict[State, State | None]', ori_state: State, dest_state: State):
    '''
    Returns a list of states that lead me from the origin state to the destination state
    '''

    # Initialize a list to store all the steps.
    # Will append the elements from the last one to the first one.
    # List initialized with the end of the sequence
    full_path = [dest_state]

    # Follow the dictionary until I get to the origin State.
    current_state = dest_state
    while current_state != ori_state:
        current_state = travel_map[current_state]
        full_path.append(current_state)

    full_path.reverse()
    return full_path


def find_solution(ori_state: State, dest_state: State):
    '''
    Gets an initial state and a final state.
    Returns the shortest sequence of states that leads from the origin to the destination.
    '''

    # Create a dictionary to store the States I came from
    # Map that associates each State with the previous State to get to it
    travel_map: dict[State, State | None] = {ori_state: None}

    # Store the states accessible from any of the already visited States
    to_visit: Queue[State] = Queue()
    to_visit.put(ori_state)

    while True:
        # If there are no States to visit this means I studied all accessible States, exit the loop
        if to_visit.empty():
            break
        # Get an element to visit.
        # As it was inserted in the que earlier than others, it needs less steps to get there.
        current_state = to_visit.get()

        # Ask all the states accessible from the current one.
        for new_state in iter_states(current_state):
            # I already have a shorter sequence to get to this State
            if new_state in travel_map:
                continue
            # It is the first I get to this State
            # Store the current_state as the previous State to get to it
            travel_map[new_state] = current_state
            # If the State is the target I stop the loop and return the full path
            if new_state == dest_state:
                return create_path(travel_map, ori_state, dest_state)

            # I found a new node accessible from this one as the shortest path
            # Store it to be visited later
            to_visit.put(new_state)

    # I visited all possible states and none of them is the target one
    raise ValueError(f"Impossible to get from:"
                     f"\n{ori_state} \nto:\n{dest_state}")


def main():
    ori_state = State([[1, None, None, None],
                       [2, None, None, None],
                       [3, 4, 5, None]])

    dest_state = State([[None, None, None, None],
                        [4, None, None, None],
                        [1, 2, 3, 5]])

    solution = find_solution(ori_state, dest_state)

    for state in solution:
        print(state)
        print()


if __name__ == '__main__':
    main()
