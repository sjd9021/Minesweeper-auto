import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):

            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """

        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        # add it as a move made
        self.moves_made.add(cell)

        # mark the current cell as safe

        if cell not in self.safes:
            self.mark_safe(cell)

        i, j = cell
        sent = set()
        # iterate over all neighboring tiles
        for a in range(max(0, i - 1), min(i + 2, self.height)):
            for b in range(max(0, j - 1), min(j + 2, self.width)):

                # Ignore the cell itself
                if (a, b) == cell:
                    continue
                # combine all neighbouring cells
                sent.add((a, b))
        # remove all safe and made moves
        sent = sent - self.safes
        sent = sent - self.moves_made
        # make a logical sentence out of the info
        sentences = Sentence(sent, count)
        self.knowledge.append(sentences)

        # check if there are any new safe cells and marking them safe
        safes = []
        for sentence in self.knowledge:
            if sentence.known_safes() is not None:
                for safety in sentence.known_safes():
                    safes.append(safety)
        for safe in safes:
            self.mark_safe(safe)
        safes.clear()

        # checking if any new confirmed mines in knowledge base
        mines = []
        for sentence in self.knowledge:
            if sentence.known_mines() is not None:
                for safety in sentence.known_mines():
                    mines.append(safety)
        for safe in mines:
            self.mark_mine(safe)
        mines.clear()

        # calling function to check for new inferences

        inferences = self.new_inferences()
        while inferences:
            for sentence in inferences:
                self.knowledge.append(sentence)

        # checking if the new inferences added can infer further new logic

            inferences = self.new_inferences()

    def make_safe_move(self):
        for i in self.safes:
            if i not in self.moves_made and i not in self.mines:
                print(i)
                self.print_data()
                return i
        return None

    def make_random_move(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                move = (i, j)
                if move not in self.mines and move not in self.moves_made:
                    self.print_data()
                    return move

        return None

    def print_data(self):
        print("Mines: ", self.mines)
        print("Knowlege: ")
        for sentence in self.knowledge:
            print("\t", sentence.cells, " = ", sentence.count)

    def new_inferences(self):
        inferences = []
        removals = []

        # for each sentence known
        for sentence1 in self.knowledge:
            # mark for removal if it is empty
            if sentence1.cells == set():
                removals.append(sentence1)
                continue
            # pick another
            for sentence2 in self.knowledge:
                # mark for removal if empty
                if sentence2.cells == set():
                    removals.append(sentence2)
                    continue
                # make sure they're different sentences
                if sentence1 != sentence2:
                    # if s2 is a subset of s1
                    if sentence2.cells.issubset(sentence1.cells):
                        diff_cells = sentence1.cells.difference(
                            sentence2.cells)
                        diff_count = sentence1.count - sentence2.count
                        # an inference can be drawn
                        new_inference = Sentence(diff_cells, diff_count)
                        if new_inference not in self.knowledge:
                            inferences.append(new_inference)

        # remove sentences without any cells
        self.knowledge = [x for x in self.knowledge if x not in removals]
        return inferences
