"""
Puzzle difficulty metrics for word ladders.
"""

import math
from collections import Counter

from utils import levenshtein_distance


def calculate_all_metrics(puzzle, word_list: set) -> dict:
    """
    Calculate all difficulty metrics for a puzzle.

    Args:
        puzzle: Either a list of (word, distance) tuples, or a dict with keys
                'solution' (list of words) and 'distances' (list of ints).
        word_list: Set of valid words (order preserved for frequency ranking).

    Returns:
        Dict of metric names to values.
    """
    if isinstance(puzzle, dict):
        solution = [w.lower() for w in puzzle['solution']]
        distances = puzzle['distances']
    else:
        solution = [w.lower() for w, _ in puzzle]
        distances = [d for _, d in puzzle[1:]]

    intermediates = solution[1:-1]
    word_list_ordered = list(word_list)

    metrics = {}

    # Path metrics
    metrics['path_length'] = len(intermediates)
    metrics['total_edit_distance'] = sum(distances)
    metrics['average_edit_distance'] = sum(distances) / len(distances) if distances else 0
    metrics['edit_distance_variance'] = _variance(distances) if len(distances) > 1 else 0

    # Word difficulty
    word_lengths = [len(w) for w in intermediates]
    metrics['average_word_length'] = sum(word_lengths) / len(word_lengths) if word_lengths else 0
    metrics['word_length_variance'] = _variance(word_lengths) if len(word_lengths) > 1 else 0
    metrics['average_word_frequency_rank'] = _average_frequency_rank(intermediates, word_list_ordered)
    metrics['rarest_word_rank'] = _rarest_word_rank(intermediates, word_list_ordered)
    metrics['average_letter_overlap_ratio'] = _average_letter_overlap(solution)

    # Search space
    metrics['average_branching_factor'] = _average_branching_factor(solution, word_list)
    unique_letters = set(''.join(intermediates))
    metrics['unique_letters_count'] = len(unique_letters)
    letter_counts = Counter(''.join(intermediates))
    metrics['letter_frequency_entropy'] = _entropy(letter_counts)
    metrics['total_letters'] = sum(len(w) for w in intermediates)

    # Constraint tightness
    metrics['min_distance_margin'] = _min_distance_margin(solution)

    # Composite score
    metrics['difficulty_score'] = calculate_difficulty_score(metrics)

    return metrics


def calculate_difficulty_score(metrics: dict) -> float:
    """
    Compute a composite difficulty score from weighted metrics.
    Higher = harder. Returns a non-negative float.
    """
    score = 0.0

    # Path complexity
    score += metrics['path_length'] * 5
    score += metrics['total_edit_distance'] * 3
    score += metrics['edit_distance_variance'] * 10

    # Word difficulty
    score += metrics['average_word_length'] * 2
    score += metrics['average_word_frequency_rank'] / 100
    score += metrics['rarest_word_rank'] / 500

    # Search space
    score -= metrics['average_branching_factor'] / 10
    score += metrics['unique_letters_count'] * 1.5
    score += metrics['letter_frequency_entropy'] * 3

    # Constraint tightness
    score -= metrics['min_distance_margin'] * 5
    score -= metrics['average_letter_overlap_ratio'] * 10

    return max(0.0, score)


def print_metrics(metrics: dict, name: str = "Puzzle"):
    """Pretty-print all metrics for a single puzzle."""
    print(f"\n{'='*60}")
    print(f"{name} Difficulty Analysis")
    print(f"{'='*60}")

    print(f"\nPath-Based Metrics:")
    print(f"  Path Length:              {metrics['path_length']}")
    print(f"  Total Edit Distance:      {metrics['total_edit_distance']}")
    print(f"  Average Edit Distance:    {metrics['average_edit_distance']:.2f}")
    print(f"  Edit Distance Variance:   {metrics['edit_distance_variance']:.2f}")

    print(f"\nWord Difficulty Metrics:")
    print(f"  Average Word Length:      {metrics['average_word_length']:.2f}")
    print(f"  Word Length Variance:     {metrics['word_length_variance']:.2f}")
    print(f"  Avg Frequency Rank:       {metrics['average_word_frequency_rank']:.0f}")
    print(f"  Rarest Word Rank:         {metrics['rarest_word_rank']}")
    print(f"  Avg Letter Overlap:       {metrics['average_letter_overlap_ratio']:.2%}")

    print(f"\nSearch Space Metrics:")
    print(f"  Avg Branching Factor:     {metrics['average_branching_factor']:.1f}")
    print(f"  Unique Letters:           {metrics['unique_letters_count']}")
    print(f"  Total Letters in Bag:     {metrics['total_letters']}")
    print(f"  Letter Entropy:           {metrics['letter_frequency_entropy']:.2f}")

    print(f"\nConstraint Metrics:")
    print(f"  Min Distance Margin:      {metrics['min_distance_margin']}")

    print(f"\nOverall Difficulty Score: {metrics['difficulty_score']:.1f}")
    print(f"{'='*60}\n")


def print_comparative_analysis(results: list):
    """Print a table comparing multiple puzzles sorted by difficulty."""
    print(f"\n{'='*80}")
    print("Comparative Puzzle Analysis")
    print(f"{'='*80}\n")

    sorted_results = sorted(results, key=lambda x: x[1]['difficulty_score'])

    print(f"{'Rank':<6} {'Puzzle':<10} {'Difficulty':<12} {'Path':<6} {'Avg Dist':<9} {'Branching':<11}")
    print('-' * 80)

    for rank, (idx, m) in enumerate(sorted_results, 1):
        print(
            f"{rank:<6} #{idx + 1:<9} {m['difficulty_score']:>10.1f}  "
            f"{m['path_length']:>4}   "
            f"{m['average_edit_distance']:>7.2f}   "
            f"{m['average_branching_factor']:>9.1f}"
        )

    print(f"\n{'='*80}\n")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _variance(values: list) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)


def _average_frequency_rank(words: list, ordered: list) -> float:
    ranks = []
    for word in words:
        try:
            ranks.append(ordered.index(word))
        except ValueError:
            ranks.append(len(ordered))
    return sum(ranks) / len(ranks) if ranks else 0.0


def _rarest_word_rank(words: list, ordered: list) -> int:
    ranks = []
    for word in words:
        try:
            ranks.append(ordered.index(word))
        except ValueError:
            ranks.append(len(ordered))
    return max(ranks) if ranks else 0


def _average_letter_overlap(solution: list) -> float:
    if len(solution) < 2:
        return 0.0
    overlaps = []
    for a, b in zip(solution, solution[1:]):
        sa, sb = set(a), set(b)
        union = len(sa | sb)
        overlaps.append(len(sa & sb) / union if union else 0.0)
    return sum(overlaps) / len(overlaps)


def _average_branching_factor(solution: list, word_list, max_edit_distance: int = 2) -> float:
    factors = []
    for i in range(len(solution) - 1):
        current = solution[i]
        next_word = solution[i + 1]
        count = sum(
            1 for w in word_list
            if w != current and w != next_word
            and 0 < levenshtein_distance(current, w) <= max_edit_distance
        )
        factors.append(count)
    return sum(factors) / len(factors) if factors else 0.0


def _entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c > 0)


def _min_distance_margin(solution: list) -> float:
    min_margin = float('inf')
    for i in range(len(solution)):
        for j in range(i + 1, len(solution) - 1):
            d_j = levenshtein_distance(solution[i], solution[j])
            d_j1 = levenshtein_distance(solution[i], solution[j + 1])
            min_margin = min(min_margin, d_j1 - d_j)
    return min_margin if min_margin != float('inf') else 0.0
