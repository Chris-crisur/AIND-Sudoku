rows = 'ABCDEFGHI'
cols = '123456789'
assignments = []


def assign_value(values: dict, box: str, value: str):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values: dict):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist:
        # more concise version to find twins below commented section
        # potential_twins = []
        # actual_twins = []
        # for u in unit:
        #     if len(values[u])==2:
        #         if potential_twins.__contains__(values[u]):
        #             actual_twins.append(values[u])
        #         else:
        #             potential_twins.append(values[u])

        # find all values that have exactly 2 possibilities
        potential_twins = [values[u] for u in unit if len(values[u]) == 2]
        # find which of the possibilities have multiple entries in the unit
        actual_twins = set([x for n, x in enumerate(potential_twins) if x in potential_twins[:n]])
        # Eliminate the naked twins as possibilities for their peers
        for twin_value in actual_twins:
            for peer in unit:  # by peers, mean peers within unit and NOT all peers
                # remove digit from peer if peer is not solved and is not the other twin
                if len(values[peer]) > 1 and values[peer] != twin_value:
                    for digit in twin_value:
                        values = assign_value(values, peer, values[peer].replace(digit, ''))

    return values


def cross(a, b):
    return [s + t for s in a for t in b]


# Define general properties of sudoku board which are used in the functions
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = list()
# rightwards facing diagonal and leftwards facing diagonal (reversed rows)
for row in [rows, rows[::-1]]:
    # convert strs to lists for zip below
    r = list(row)
    c = list(cols)
    d = ['%s%s' % t for t in zip(r, c)]
    diagonal_units.append(d)
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def display(values: dict):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)


def grid_values(grid: str):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = ['123456789' if g == '.' else g for g in grid]
    assert len(grid) == 81
    return dict(zip(boxes, chars))
    # solution.py version:
    # values = []
    # all_digits = '123456789'
    # for c in grid:
    #     if c == '.':
    #         values.append(all_digits)
    #     elif c in all_digits:
    #         values.append(c)
    # assert len(values) == 81
    # return dict(zip(boxes, values))


def eliminate(values: dict):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(digit, ''))
    return values


def only_choice(values: dict):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        # create a dict of digits to count appearances
        digits = dict(zip('123456789', [list([]) for _ in range(9)]))
        for u in unit:
            for digit in values[u]:
                digits[digit].append(u)
        for digit, box_list in digits.items():
            if len(box_list) == 1:
                values = assign_value(values, box_list[0], digit)
    return values
    # solution.py version:
    # for unit in unitlist:
    #     for digit in '123456789':
    #         dplaces = [box for box in unit if digit in values[box]]
    #         if len(dplaces) == 1:
    #             assign_value(values,dplaces[0],digit)
    # return values


def reduce_puzzle(values: dict):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values: dict):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid: str):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)
    return values


def validateSum(values: dict):
    return sum([sum(int(values[u]) for u in units) for units in unitlist]) == 45 * len(unitlist)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
