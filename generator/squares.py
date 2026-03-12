#!/usr/bin/env python3
"""
Command-line tool for finding double word square solutions.

Subcommands:
    find   Find N solutions automatically (default: 5)
    run    Run continuously, saving solutions to files
    test   Test the solver with a row constraint

Usage:
    python squares.py find [--count N]
    python squares.py run [--max N] [--output FILE] [--json FILE] [--constraint WORD]
    python squares.py test [--row ROW] [--word WORD]
"""

import argparse
import json
import time
from datetime import datetime

from word_square import DoubleWordSquareSolver


# ---------------------------------------------------------------------------
# find subcommand
# ---------------------------------------------------------------------------

def cmd_find(args):
    solver = DoubleWordSquareSolver()
    if not solver.words:
        return

    print(f"\n{'='*60}")
    print(f"Finding {args.count} double word square solutions")
    print(f"{'='*60}\n")

    for i in range(args.count):
        print(f"\n{'='*60}")
        print(f"Solution #{i + 1}")
        print(f"{'='*60}")
        result = solver.solve() if i == 0 else solver.find_next_solution()
        if result:
            solver.print_solution(*result)
            print(f"\nTotal found so far: {len(solver.previous_solutions)}")
        else:
            print(f"No more solutions after {i}.")
            break

    print(f"\n{'='*60}")
    print(f"Found {len(solver.previous_solutions)} solutions total")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# run subcommand
# ---------------------------------------------------------------------------

def cmd_run(args):
    starting_grid = None
    if args.constraint:
        word = args.constraint.upper()
        if len(word) == 5:
            starting_grid = [list(word)] + [['', '', '', '', ''] for _ in range(4)]
            print(f"Constraint: first row = '{word}'")
        else:
            print("Constraint must be a 5-letter word; ignoring.")

    solver = DoubleWordSquareSolver()
    if not solver.words:
        return

    with open(args.output, 'w') as f:
        f.write("DOUBLE WORD SQUARE SOLUTIONS\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

    solutions_data = []
    count = 0
    total_start = time.time()

    print(f"\n{'='*70}")
    print("CONTINUOUS DOUBLE WORD SQUARE SOLVER")
    print(f"{'='*70}")
    print(f"Saving to: {args.output} / {args.json}")
    if args.max:
        print(f"Will find up to {args.max} solutions")
    else:
        print("Running until exhausted or Ctrl+C")
    print()

    try:
        while True:
            if args.max and count >= args.max:
                print(f"Reached limit of {args.max} solutions.")
                break

            print(f"\n{'='*70}")
            print(f"Searching for solution #{count + 1}...")

            search_start = time.time()
            result = solver.solve(starting_grid) if count == 0 else solver.find_next_solution(starting_grid)
            search_time = time.time() - search_start

            if result is None:
                print(f"\nNo more solutions after {count}.")
                break

            count += 1
            row_words, col_words = result
            print(f"\nSolution #{count} found in {search_time:.2f}s")
            print("Grid:")
            for word in row_words:
                print("  " + " ".join(word))
            print(f"Rows: {', '.join(row_words)}")
            print(f"Cols: {', '.join(col_words)}")

            stats = {'search_time': search_time, 'nodes': solver.nodes_explored, 'backtracks': solver.backtracks}
            _append_solution_text(args.output, count, row_words, col_words, stats)
            solutions_data.append({
                'solution_number': count,
                'timestamp': datetime.now().isoformat(),
                'row_words': row_words,
                'col_words': col_words,
                'search_stats': stats,
            })
            with open(args.json, 'w') as f:
                json.dump(solutions_data, f, indent=2)

            elapsed = time.time() - total_start
            print(f"Progress: {count} solutions in {elapsed:.1f}s ({elapsed/count:.2f}s avg)")

    except KeyboardInterrupt:
        print("\n\nStopped by user.")

    total = time.time() - total_start
    print(f"\n{'='*70}")
    print(f"Done: {count} solutions in {total:.1f}s")
    if count:
        print(f"Average: {total/count:.2f}s per solution")
    print(f"{'='*70}")


def _append_solution_text(filename, number, row_words, col_words, stats):
    with open(filename, 'a') as f:
        f.write("="*70 + "\n")
        f.write(f"SOLUTION #{number}\n")
        f.write(f"Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Time: {stats['search_time']:.2f}s, Nodes: {stats['nodes']}, Backtracks: {stats['backtracks']}\n")
        f.write("="*70 + "\n\n")
        f.write("Grid:\n")
        for word in row_words:
            f.write("  " + " ".join(word) + "\n")
        f.write("\nRows:\n")
        for i, word in enumerate(row_words):
            f.write(f"  Row {i+1}: {word}\n")
        f.write("\nCols:\n")
        for i, word in enumerate(col_words):
            f.write(f"  Col {i+1}: {word}\n")
        f.write("\n\n")


# ---------------------------------------------------------------------------
# test subcommand
# ---------------------------------------------------------------------------

def cmd_test(args):
    solver = DoubleWordSquareSolver()
    if not solver.words:
        return

    word = args.word.upper()
    row = args.row - 1  # Convert to 0-indexed

    if len(word) != 5:
        print(f"Error: word must be 5 letters (got '{word}')")
        return
    if not 1 <= args.row <= 5:
        print(f"Error: row must be 1–5 (got {args.row})")
        return

    grid = [['', '', '', '', ''] for _ in range(5)]
    grid[row] = list(word)

    print(f"\nTesting with row {args.row} = '{word}'")
    result = solver.solve(grid)
    if result:
        solver.print_solution(*result)
    else:
        print("No solution found with this constraint.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Double word square solver CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # find
    p_find = sub.add_parser('find', help='Find N solutions automatically')
    p_find.add_argument('--count', type=int, default=5, help='Number of solutions to find')

    # run
    p_run = sub.add_parser('run', help='Run continuously, saving solutions to files')
    p_run.add_argument('--max', '-m', type=int, default=None, help='Max solutions (default: unlimited)')
    p_run.add_argument('--output', '-o', default='solutions.txt', help='Text output file')
    p_run.add_argument('--json', '-j', default='solutions.json', help='JSON output file')
    p_run.add_argument('--constraint', '-c', default=None, help='5-letter word to fix as first row')

    # test
    p_test = sub.add_parser('test', help='Test with a row constraint')
    p_test.add_argument('--row', type=int, default=2, help='Which row to constrain (1–5, default: 2)')
    p_test.add_argument('--word', default='TABOO', help='Word to place in that row')

    args = parser.parse_args()

    if args.command == 'find':
        cmd_find(args)
    elif args.command == 'run':
        cmd_run(args)
    elif args.command == 'test':
        cmd_test(args)


if __name__ == "__main__":
    main()
