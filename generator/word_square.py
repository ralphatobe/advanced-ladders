"""
Double word square solver.

A double word square is a 5x5 grid where every row and every column
spells a valid word, with the row words and column words being different
(not a regular word square).
"""

from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict
import time


class DoubleWordSquareSolver:
    def __init__(self, word_file: str = "data/square_words.txt"):
        """Initialize the solver with a word list."""
        self.size = 5
        self.words = self._load_words(word_file)
        self.word_set = set(self.words)
        self.prefixes = self._build_prefix_set()
        self.words_by_first_letter = self._index_by_first_letter()

        self.nodes_explored = 0
        self.backtracks = 0
        self.previous_solutions: List[Tuple] = []
        self.solution_generator = None
        self.starting_grid_for_generator = None

    def _load_words(self, filename: str) -> List[str]:
        words = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    word = line.strip().upper()
                    if len(word) == self.size and word.isalpha():
                        words.append(word)
        except FileNotFoundError:
            print(f"Error: Could not find {filename}")
            print("Please provide a file with 5-letter words, one per line.")
            return []
        print(f"Loaded {len(words)} valid 5-letter words")
        return words

    def _build_prefix_set(self) -> Set[str]:
        prefixes = set()
        for word in self.words:
            for i in range(1, len(word) + 1):
                prefixes.add(word[:i])
        return prefixes

    def _index_by_first_letter(self) -> Dict[str, List[str]]:
        index = defaultdict(list)
        for word in self.words:
            index[word[0]].append(word)
        return index

    def solve(
        self, starting_grid: Optional[List[List[str]]] = None
    ) -> Optional[Tuple[List[str], List[str]]]:
        """
        Find the first valid double word square.

        Args:
            starting_grid: Optional 5x5 grid (use '' for empty cells).

        Returns:
            (row_words, col_words) tuple, or None if no solution found.
        """
        print("\nStarting search for double word square...")

        self.nodes_explored = 0
        self.backtracks = 0
        self.starting_grid_for_generator = starting_grid

        if starting_grid is None:
            grid = [['' for _ in range(self.size)] for _ in range(self.size)]
        else:
            if len(starting_grid) != self.size or any(len(r) != self.size for r in starting_grid):
                print(f"Error: Starting grid must be {self.size}x{self.size}")
                return None
            grid = [row[:] for row in starting_grid]
            print("\nStarting grid:")
            self._print_grid(grid)

        row_words = [''] * self.size
        col_words = [''] * self.size

        for i in range(self.size):
            if all(grid[i][j] != '' for j in range(self.size)):
                word = ''.join(grid[i][j] for j in range(self.size))
                if word in self.word_set:
                    row_words[i] = word
                else:
                    print(f"Warning: Row {i+1} ('{word}') is not a valid word")

        start_row = next((i for i in range(self.size) if row_words[i] == ''), 0)

        start_time = time.time()
        self.solution_generator = self._backtrack(grid, row_words, col_words, start_row)

        return self._get_next(start_time, record=True)

    def find_next_solution(
        self, starting_grid: Optional[List[List[str]]] = None
    ) -> Optional[Tuple[List[str], List[str]]]:
        """
        Continue the search for additional solutions beyond the first.

        If starting_grid differs from the previous call, starts a fresh search.
        """
        if self.solution_generator is None or starting_grid != self.starting_grid_for_generator:
            return self.solve(starting_grid)

        print("\nContinuing search for next solution...")
        start_nodes = self.nodes_explored
        start_backtracks = self.backtracks
        start_time = time.time()

        result = self._get_next(start_time, record=True)

        nodes_used = self.nodes_explored - start_nodes
        backs_used = self.backtracks - start_backtracks
        print(f"Nodes explored: {nodes_used}, Backtracks: {backs_used}")

        return result

    def reset_solutions(self):
        """Clear all previously found solutions so they can be found again."""
        self.previous_solutions = []
        print("Cleared all previous solutions.")

    def print_solution(self, row_words: List[str], col_words: List[str]):
        """Display a solution in a human-readable format."""
        print("\n" + "="*50)
        print("DOUBLE WORD SQUARE FOUND!")
        print("="*50)

        print("\nGrid:")
        for word in row_words:
            print(f"  {' '.join(word)}")

        print("\nHorizontal words (rows):")
        for i, word in enumerate(row_words):
            print(f"  Row {i+1}: {word}")

        print("\nVertical words (columns):")
        for i, word in enumerate(col_words):
            print(f"  Col {i+1}: {word}")

        all_words = row_words + col_words
        print("\nVerification:")
        if len(set(all_words)) == len(all_words):
            print("  All 10 words are unique")
        else:
            print("  Some words are repeated")
        if all(w in self.word_set for w in all_words):
            print("  All words are valid")
        else:
            print("  Some words are invalid")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_next(self, start_time: float, record: bool = False):
        try:
            result = next(self.solution_generator)
            elapsed = time.time() - start_time
            print(f"\nSearch completed in {elapsed:.2f}s")
            print(f"Nodes explored: {self.nodes_explored}, Backtracks: {self.backtracks}")
            if result and record:
                self.previous_solutions.append((tuple(result[0]), tuple(result[1])))
            return result
        except StopIteration:
            elapsed = time.time() - start_time
            print(f"\nSearch exhausted in {elapsed:.2f}s — no more solutions.")
            self.solution_generator = None
            return None

    def _print_grid(self, grid: List[List[str]]):
        for row in grid:
            print("  " + " ".join(c if c else '.' for c in row))

    def _backtrack(
        self,
        grid: List[List[str]],
        row_words: List[str],
        col_words: List[str],
        row_idx: int,
    ):
        self.nodes_explored += 1

        if self.nodes_explored % 10000 == 0:
            print(f"Explored {self.nodes_explored} nodes...", end='\r')

        if row_idx == self.size:
            # Verify all columns form valid words
            for col_idx in range(self.size):
                col_word = ''.join(grid[r][col_idx] for r in range(self.size))
                if col_word not in self.word_set:
                    return
                col_words[col_idx] = col_word

            # Must be a true double word square (rows != columns)
            if all(row_words[i] == col_words[i] for i in range(self.size)):
                return

            solution = (tuple(row_words), tuple(col_words))
            if solution in self.previous_solutions:
                return

            yield (row_words.copy(), col_words.copy())
            return

        for word in self._candidates_for_row(grid, row_idx, row_words, col_words):
            original = {j: grid[row_idx][j] for j in range(self.size) if grid[row_idx][j] != ''}

            for j in range(self.size):
                if j not in original:
                    grid[row_idx][j] = word[j]
            row_words[row_idx] = word

            if self._is_consistent(grid, row_idx):
                yield from self._backtrack(grid, row_words, col_words, row_idx + 1)

            self.backtracks += 1
            for j in range(self.size):
                if j not in original:
                    grid[row_idx][j] = ''
            row_words[row_idx] = ''

    def _is_consistent(self, grid: List[List[str]], row_idx: int) -> bool:
        for col_idx in range(self.size):
            prefix = ''.join(grid[r][col_idx] for r in range(row_idx + 1))
            if prefix not in self.prefixes:
                return False
        return True

    def _candidates_for_row(
        self,
        grid: List[List[str]],
        row_idx: int,
        row_words: List[str],
        col_words: List[str],
    ) -> List[str]:
        # If the row is already fully specified, validate and return it
        if all(grid[row_idx][j] != '' for j in range(self.size)):
            word = ''.join(grid[row_idx][j] for j in range(self.size))
            return [word] if word in self.word_set else []

        required = {j: grid[row_idx][j] for j in range(self.size) if grid[row_idx][j] != ''}
        used_row_words = {w for w in row_words if w}
        candidates = [w for w in self.words if w not in used_row_words]

        # Filter by fixed positions
        for pos, char in required.items():
            candidates = [w for w in candidates if w[pos] == char]

        # Filter by column prefix validity
        for col_idx in range(self.size):
            col_prefix = ''.join(grid[r][col_idx] for r in range(row_idx))
            valid = []
            for word in candidates:
                new_prefix = col_prefix + word[col_idx]
                if new_prefix in self.prefixes:
                    if row_idx == self.size - 1:
                        if new_prefix in self.word_set and new_prefix not in col_words:
                            valid.append(word)
                    else:
                        valid.append(word)
            candidates = valid
            if not candidates:
                return []

        return candidates
