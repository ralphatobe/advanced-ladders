"""
Shared utilities for puzzle generation.
"""
from __future__ import annotations


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the minimum edit distance between two strings."""
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if s1[i - 1] == s2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    return dp[n]


def load_dictionary(filepath: str, limit: int = None) -> set:
    """
    Load a word list from a .txt or .csv file.

    Args:
        filepath: Path to the dictionary file.
        limit: If set, only the first `limit` words are returned.

    Returns:
        A set of lowercase alphabetic words, or None on error.
    """
    ext = filepath.rsplit('.', 1)[-1].lower()
    try:
        with open(filepath, 'r') as f:
            if ext == 'txt':
                words = [line.strip().lower() for line in f if line.strip().isalpha()]
            elif ext == 'csv':
                f.readline()  # skip header
                words = [line.split(',')[0].strip().lower() for line in f if line.strip()]
            else:
                print(f"Unsupported file extension: .{ext}")
                return None
    except FileNotFoundError:
        print(f"Dictionary file not found: {filepath}")
        return None

    if limit:
        words = words[:limit]
    result = set(words)
    print(f"Loaded {len(result)} words from {filepath}")
    return result
