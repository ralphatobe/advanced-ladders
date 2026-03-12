"""
Word ladder algorithms.

Provides three approaches:
- find_ladder: BFS for classic single-edit ladders
- find_variable_ladder: A* search allowing up to max_edit_distance per step
- generate_variable_ladder: Random generation with non-decreasing distance constraint
"""

from __future__ import annotations

import heapq
import random
from collections import deque

from utils import levenshtein_distance


# ---------------------------------------------------------------------------
# Classic BFS ladder (single-character edits only)
# ---------------------------------------------------------------------------

def find_ladder(
    start: str,
    end: str,
    word_list,
) -> list[tuple] | None:
    """
    Find a word ladder using BFS where each step changes exactly one character.

    Args:
        start: Starting word.
        end: Target word.
        word_list: Collection of valid words.

    Returns:
        List of (word, edit_distance) tuples, or None if no path exists.
        The first entry always has distance 0.
    """
    start, end = start.lower(), end.lower()
    word_set = set(word_list)
    word_set.add(start)
    word_set.add(end)

    if start == end:
        return [(start, 0)]

    # Only consider same-length words for single-edit BFS
    candidates = {w for w in word_set if len(w) == len(start)}

    queue = deque([(start, [(start, 0)])])
    visited = {start}

    while queue:
        current, path = queue.popleft()
        for word in candidates:
            if word in visited:
                continue
            if levenshtein_distance(current, word) == 1:
                new_path = path + [(word, 1)]
                if word == end:
                    return new_path
                visited.add(word)
                queue.append((word, new_path))

    return None


# ---------------------------------------------------------------------------
# A* variable-length ladder
# ---------------------------------------------------------------------------

def find_variable_ladder(
    start: str,
    end: str,
    word_list,
    max_edit_distance: int = 2,
) -> list[tuple] | None:
    """
    Find a word ladder using A* where each step allows up to max_edit_distance edits.

    Args:
        start: Starting word.
        end: Target word.
        word_list: Collection of valid words.
        max_edit_distance: Maximum edit distance allowed per step.

    Returns:
        List of (word, edit_distance) tuples, or None if no path exists.
    """
    start, end = start.lower(), end.lower()
    word_set = set(word_list)
    word_set.add(start)
    word_set.add(end)

    if start == end:
        return [(start, 0)]

    min_len = min(len(start), len(end), 4)
    max_len = max(len(start), len(end)) + max_edit_distance
    candidates = {w for w in word_set if min_len <= len(w) <= max_len}

    print(f"Searching through {len(candidates)} candidate words (filtered from {len(word_set)})")

    pq = [(levenshtein_distance(start, end), 0, start, [(start, 0)])]
    visited = {}
    nodes_explored = 0

    while pq:
        _, total_dist, current, path = heapq.heappop(pq)

        if current in visited:
            continue
        visited[current] = total_dist
        nodes_explored += 1

        if nodes_explored % 1000 == 0:
            print(f"Explored {nodes_explored} nodes...")

        if current == end:
            print(f"Found path of length {total_dist}! Explored {nodes_explored} nodes.")
            return path

        for word in candidates:
            if word in visited:
                continue
            dist = levenshtein_distance(current, word)
            if 0 < dist <= max_edit_distance:
                new_total = total_dist + dist
                heuristic = levenshtein_distance(word, end)
                heapq.heappush(pq, (new_total + heuristic, new_total, word, path + [(word, dist)]))

        # Keep beam narrow to stay tractable
        pq = pq[:1000]

    print(f"No path found. Explored {nodes_explored} nodes.")
    return None


# ---------------------------------------------------------------------------
# Random ladder generation with non-decreasing distance constraint
# ---------------------------------------------------------------------------

def generate_variable_ladder(
    word_list,
    start_word: str = None,
    ladder_length: int = 6,
    max_edit_distance: int = None,
    max_attempts: int = 1000,
    verbose: bool = False,
) -> list[tuple] | None:
    """
    Randomly build a word ladder where distances from each word to later words
    are non-decreasing.

    Args:
        word_list: Collection of valid words.
        start_word: Starting word (chosen randomly if None).
        ladder_length: Total number of words in the ladder.
        max_edit_distance: Maximum edit distance per consecutive step (None = unlimited).
        max_attempts: Number of random restarts before giving up.
        verbose: Print progress messages.

    Returns:
        List of (word, distance_from_previous) tuples, or None if generation failed.
    """
    word_set = set(word_list)
    if start_word:
        start_word = start_word.lower()
    else:
        start_word = random.choice(list(word_list)).lower()
    word_set.add(start_word)

    if ladder_length <= 1:
        return [(start_word, 0)] if ladder_length == 1 else None

    for _ in range(max_attempts):
        ladder = [(start_word, 0)]
        used = {start_word}

        while len(ladder) < ladder_length:
            current, _ = ladder[-1]
            candidates = []

            for word in word_set:
                if word in used:
                    continue
                dist_current = levenshtein_distance(current, word)
                if max_edit_distance is not None and dist_current > max_edit_distance:
                    continue

                # Non-decreasing constraint: distances from each prior word must increase
                valid = True
                for i, (prev_word, _) in enumerate(ladder[:-1]):
                    if levenshtein_distance(prev_word, word) <= levenshtein_distance(prev_word, current):
                        valid = False
                        break
                if valid:
                    candidates.append(word)

            if not candidates:
                break  # Dead end — restart

            next_word = random.choice(candidates)
            ladder.append((next_word, levenshtein_distance(current, next_word)))
            used.add(next_word)

        if len(ladder) == ladder_length:
            if verbose:
                print(f"Generated ladder of length {ladder_length}")
            return ladder

    if verbose:
        print(f"Could not generate a ladder of length {ladder_length} after {max_attempts} attempts")
    return None
