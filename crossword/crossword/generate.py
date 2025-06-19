import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.crossword.variables:
            self.domains[variable] = set([x for x in self.domains[variable] if len(x) == variable.length])
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changed = False
        same_letter = self.crossword.overlaps[(x, y)]
        xdomain = list(self.domains[x])
        for poss_val in xdomain:
            if all(poss_val[same_letter[0]] != valy[same_letter[1]] for valy in self.domains[y]):
                    changed = True
                    self.domains[x].remove(poss_val)
        return changed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [(x, y) for (x, y) in list(self.crossword.overlaps.keys()) if self.crossword.overlaps[(x, y)] is not None]
        while arcs:
            (x, y) = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = [y2 for (x2, y2) in list(self.crossword.overlaps.keys())
                             if x2 == x and y2 != y and self.crossword.overlaps[(x2, y2)] is not None]
                for variable in neighbors:
                    if (variable,x) not in arcs:
                        arcs.append((variable,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable in assignment.keys():
                continue
            else:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable in assignment.keys():
                if len(assignment[variable]) != variable.length:
                    return False
        for var1, var2 in self.crossword.overlaps.keys():
            if var1 in assignment.keys() and var2 in assignment.keys() and self.crossword.overlaps[(var1, var2)] is not None:
                if assignment[var1][self.crossword.overlaps[(var1, var2)][0]] != \
                    assignment[var2][self.crossword.overlaps[(var1, var2)][1]]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors_unassigned = [y for (x, y) in list(self.crossword.overlaps.keys())
                     if x == var and y not in assignment.keys() and self.crossword.overlaps[(x, y)] is not None]
        ordered_domain_values = dict()
        for val in self.domains[var]:
            ordered_domain_values[val] = 0
            for neighbor in neighbors_unassigned:
                for valy in self.domains[neighbor]:
                    if val[self.crossword.overlaps[(var, neighbor)][0]] != valy[self.crossword.overlaps[(var, neighbor)][1]]:
                        ordered_domain_values[val] += 1
        ordered_domain_values = [k for k, v in sorted(ordered_domain_values.items(), key=lambda item: item[1])]
        return ordered_domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [x for x in self.crossword.variables if x not in assignment.keys()]
        ordered = list()
        minimum = 6e10
        for var in unassigned:
            if len(self.domains[var]) < minimum:
                minimum = len(self.domains[var])
                ordered = [var]
            elif len(self.domains[var]) == minimum:
                ordered.append(var)
        if len(ordered) > 1:
            max_degree = 0
            ordered1 = list()
            for var in ordered:
                neighbors = [y for (x, y) in list(self.crossword.overlaps.keys())
                         if x == var and self.crossword.overlaps[(x, y)] is not None]
                if len(neighbors) > max_degree:
                    max_degree = len(neighbors)
                    ordered1 = [var]
                elif len(neighbors) == max_degree:
                    ordered1.append(var)
            return ordered1[0]
        else:
            return ordered[0]



    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            temp = assignment
            temp[var] = value
            if self.consistent(temp):
                assignment = temp
                neighbors = [y for (x, y) in list(self.crossword.overlaps.keys())
                             if x == var and self.crossword.overlaps[(x, y)] is not None]
                arcs = []
                for neigh in neighbors:
                    arcs.append((var, neigh))
                if arcs:
                    self.ac3(arcs=arcs)
                result = self.backtrack(assignment)
                if result:
                    return assignment
            assignment.pop(var)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
