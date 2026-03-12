#!/usr/bin/env python3
"""
Generate word ladder puzzles and save them to puzzles.json.

Usage:
    python generate.py
    python generate.py --count 50 --output my_puzzles.json
"""

import argparse
import json
import random

from ladder import find_variable_ladder
from metrics import calculate_all_metrics
from utils import levenshtein_distance, load_dictionary


def find_word_pairs(
    word_list,
    min_distance: int = 4,
    max_distance: int = 8,
    num_pairs: int = 50,
) -> list:
    """
    Find pairs of words of different lengths with Levenshtein distance in (min, max).

    Returns:
        List of (word1, word2, distance) tuples.
    """
    words_by_length = {}
    for word in word_list:
        length = len(word)
        if 3 <= length <= 10:
            words_by_length.setdefault(length, []).append(word)

    # Cap each bucket to avoid excessive computation
    for length in words_by_length:
        if len(words_by_length[length]) > 100:
            words_by_length[length] = random.sample(words_by_length[length], 100)

    pairs = []
    lengths = sorted(words_by_length)

    for i, len1 in enumerate(lengths):
        for len2 in lengths[i + 2:]:  # skip adjacent lengths for variety
            if abs(len1 - len2) > 6:
                continue
            bucket1 = words_by_length[len1][:]
            bucket2 = words_by_length[len2][:]
            random.shuffle(bucket1)
            random.shuffle(bucket2)
            for w1, w2 in zip(bucket1, bucket2):
                dist = levenshtein_distance(w1, w2)
                if min_distance < dist < max_distance:
                    pairs.append((w1, w2, dist))
                    if len(pairs) >= num_pairs:
                        return pairs

    return pairs


def generate_puzzles(
    dictionary_file: str = 'data/words.txt',
    num_puzzles: int = 30,
) -> list:
    """
    Generate word ladder puzzles.

    Args:
        dictionary_file: Path to the word list file.
        num_puzzles: Number of puzzles to produce.

    Returns:
        List of puzzle dicts with keys: start, end, solution, wordLengths, distances.
    """
    print("Loading dictionary...")
    word_list = load_dictionary(dictionary_file)
    if not word_list:
        return []

    print(f"\nFinding word pairs (distance 4–9)...")
    candidates = find_word_pairs(word_list, min_distance=4, max_distance=9, num_pairs=200)

    if len(candidates) < 30:
        print("Too few pairs — relaxing constraints...")
        candidates += find_word_pairs(word_list, min_distance=2, max_distance=10, num_pairs=150)

    print(f"Found {len(candidates)} candidate pairs")
    print(f"\nGenerating {num_puzzles} puzzles...")

    puzzles = []
    used_words: set = set()
    used_indices: set = set()
    attempts = 0
    max_attempts = min(len(candidates) * 3, 300)

    while len(puzzles) < num_puzzles and attempts < max_attempts:
        available = [
            (i, w1, w2) for i, (w1, w2, _) in enumerate(candidates)
            if i not in used_indices and w1 not in used_words and w2 not in used_words
        ]
        if not available:
            print("No more available word pairs.")
            break

        i, w1, w2 = random.choice(available)
        used_indices.add(i)
        attempts += 1

        print(f"\nPuzzle {len(puzzles) + 1}: '{w1}' -> '{w2}'")
        path = find_variable_ladder(w1, w2, word_list, max_edit_distance=2)

        if path and len(path) > 6:
            m = calculate_all_metrics(path, word_list)
            print(f"  Found: {len(path)-1} steps, difficulty {m['difficulty_score']:.1f}")
            puzzles.append({
                'start': w1.upper(),
                'end': w2.upper(),
                'solution': [w.upper() for w, _ in path],
                'wordLengths': [len(w) for w, _ in path],
                'distances': [d for _, d in path[1:]],
            })
            used_words.add(w1)
            used_words.add(w2)
        elif path:
            print(f"  Skipped: solution too short ({len(path)-1} steps)")
        else:
            print("  Skipped: no solution found")

    if len(puzzles) < num_puzzles:
        print(f"\nWarning: Generated {len(puzzles)}/{num_puzzles} puzzles")

    return puzzles


def save_puzzles(puzzles: list, output_file: str = 'puzzles.json'):
    with open(output_file, 'w') as f:
        json.dump(puzzles, f, indent=2)
    print(f"\nSaved {len(puzzles)} puzzles to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate word ladder puzzles")
    parser.add_argument('--count', type=int, default=30, help='Number of puzzles to generate')
    parser.add_argument('--output', default='puzzles.json', help='Output JSON file')
    parser.add_argument('--dict', default='data/words.txt', help='Dictionary file path')
    args = parser.parse_args()

    puzzles = generate_puzzles(dictionary_file=args.dict, num_puzzles=args.count)
    if puzzles:
        save_puzzles(puzzles, args.output)
    else:
        print("Failed to generate puzzles. Check your dictionary file.")


if __name__ == "__main__":
    main()
