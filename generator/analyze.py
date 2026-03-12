#!/usr/bin/env python3
"""
Analyze difficulty metrics for a set of word ladder puzzles.

Usage:
    python analyze.py
    python analyze.py --dict data/words.txt
"""

import argparse

from metrics import calculate_all_metrics, print_metrics, print_comparative_analysis
from utils import load_dictionary

# Sample puzzles for analysis (tuples of (word, edit_distance))
SAMPLE_PUZZLES = [
    [('slow', 0), ('salon', 2), ('satin', 2), ('seating', 2), ('heading', 2), ('headline', 2)],
    [('mart', 0), ('bare', 2), ('lane', 2), ('lance', 1), ('lone', 2), ('none', 1), ('long', 2),
     ('losing', 2), ('posing', 1), ('pissing', 2), ('fisting', 2), ('testing', 2), ('destiny', 2), ('destroy', 2)],
    [('brain', 0), ('bargain', 2), ('margin', 2), ('virgin', 2), ('virginia', 2)],
    [('aged', 0), ('amend', 2), ('attend', 2), ('extend', 2), ('exceed', 2), ('excess', 2),
     ('access', 2), ('success', 2), ('succeed', 2)],
    [('soul', 0), ('song', 2), ('sing', 1), ('saving', 2), ('skating', 2), ('seating', 1),
     ('serving', 2), ('service', 2), ('survive', 2)],
    [('cause', 0), ('caused', 1), ('causes', 1), ('cruises', 2), ('crisis', 2), ('critics', 2),
     ('clinics', 2), ('clinic', 1)],
    [('kind', 0), ('pins', 2), ('pros', 2), ('promo', 2), ('prompt', 2), ('promptly', 2)],
    [('boat', 0), ('born', 2), ('boring', 2), ('losing', 2), ('hosting', 2), ('hunting', 2)],
    [('vast', 0), ('east', 1), ('seas', 2), ('sees', 1), ('steel', 2), ('stereo', 2)],
]


def analyze_puzzles(puzzles: list, word_list: set) -> list:
    results = []
    for i, puzzle in enumerate(puzzles):
        start = puzzle[0][0].upper()
        end = puzzle[-1][0].upper()
        print(f"\n{'='*70}")
        print(f"Analyzing Puzzle {i+1}: {start} -> {end}")
        print(f"{'='*70}")
        m = calculate_all_metrics(puzzle, word_list)
        print_metrics(m, f"Puzzle {i+1}: {start} -> {end}")
        results.append((i, m))
    return results


def print_summary(results: list):
    print("\n" + "="*80)
    print("Summary Statistics")
    print("="*80)

    difficulties = [m['difficulty_score'] for _, m in results]
    paths = [m['path_length'] for _, m in results]
    avg_lengths = [m['average_word_length'] for _, m in results]
    branchings = [m['average_branching_factor'] for _, m in results]

    for label, values in [
        ("Difficulty Scores", difficulties),
        ("Path Lengths", paths),
        ("Average Word Lengths", avg_lengths),
        ("Average Branching Factors", branchings),
    ]:
        print(f"\n{label}:")
        print(f"  Range: {min(values):.2f} - {max(values):.2f}")
        print(f"  Mean:  {sum(values)/len(values):.2f}")

    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description="Analyze word ladder puzzle difficulty")
    parser.add_argument('--dict', default='data/words.txt', help='Dictionary file')
    args = parser.parse_args()

    print("Loading dictionary...")
    words = load_dictionary(args.dict)
    if not words:
        print("Error: Could not load dictionary")
        return

    results = analyze_puzzles(SAMPLE_PUZZLES, words)
    print_comparative_analysis(results)
    print_summary(results)


if __name__ == "__main__":
    main()
