assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    # Cross product of elements in A and elements in B.
    return [s+t for s in A for t in B]

def diagonalCross(A):
    """
    Create two extra units, the diagonals of the board, to solve Diagonal Sudoku
    Args:
        The rows of the Sudoku in unique string form.
    Returns:
        Diagonal units list
            Keys: The boxes, e.g., 'A1'
    """
    d1 = []
    d2 = []
    diagonalUnits = []
    # Create the first diagonal unit
    index = 1
    for s in A:
        d1.append(s+str(index))
        index += 1
    diagonalUnits.append(d1)
    index = 9
    # Create the second diagonal unit
    for s in A:
        d2.append(s+str(index))
        index = index - 1  
    diagonalUnits.append(d2)
    return diagonalUnits


# Name of each box in the sudoku grid
boxes = cross(rows,cols)
# Units and other aggrupations of boxes
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units= diagonalCross(rows)
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    # Contains the grid in form of a dictionary
    dictGrid = {}
    # Current index position in the boxes(Sudoku grid) string 
    index = 0
    # Go through each char in the grid string to create its correspongin (key,value) pair and add it to the dictionary
    for value in grid:
        if value == '.':
            dictGrid.update({boxes[index] : '123456789'})
        else:
            dictGrid.update({boxes[index] : value})
        # Increment the index to go to the next box in boxes
        index += 1
    return dictGrid

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Explore every unit looking for naked twins
    unitlist2 = row_units + column_units + square_units
    for unit in unitlist2:
        # Find all naked twins in a unit
        twins = []
        twinsPairs = []
        twinsPairsMainElement = []
        for box in unit:
            for boxj in unit:
                if ((values[box] == values[boxj]) and (box != boxj))and(len(values[box])==2):
                    admittet = True
                    for p in twinsPairsMainElement:
                        if (p == box) or (p == boxj):
                            admittet = False
                            break
                    if admittet:
                        twinsPairsMainElement.append(box)
                        twins = [box,boxj]
                        twinsPairs.append(twins)
        
        
        # Eliminate from the peers of the naked twins in the unit the numbers of the naked twins
        for twin in twinsPairsMainElement:
            for box in unit:
                if (values[twin] != values[box])and(len(values[box])>1):
                    for number in values[twin]:
                        if values[box].find(number) > -1:
                            assign_value(values,box,values[box].replace(number,''))

    return values

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Elimination strategy. If a box has a value assigned, then none of the peers 
    of this box can have this value.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """
    solved = []
    for key, value in values.items():
        if len(value) == 1:
            solved.append(key)
    for box in solved:
        for peer in peers[box]:
            assign_value(values,peer,values[peer].replace(values[box],''))
    return values

def only_choice(values):
    """
    Only choice strategy. If there is only one box in a unit which would allow 
    a certain digit, then that box must be assigned that digit
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """
    new_values = values.copy()  # note: do not modify original values
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                new_values[dplaces[0]] = digit
    return new_values

def reduce_puzzle(values):
    """
    Constraint propagation. Alternate between the elimition and only choice
    strategy to solve the sudoku 
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Use Depth Firts Search to solve the Sudoku 
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku,s,value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))



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
