from vigenere_crack import (
    CIPHERTEXT,
    find_key_letter,
    decrypt_vigenere,
    index_of_coincidence,
)

KEY_LENGTH = 14

SCORE_WORDS = [
    "the",
    "and",
    "ing",
    "her",
    "hat",
    "his",
    "not",
    "tha",
    "ere",
    "for",
    "all",
    "was",
    "but",
    "are",
    "ith",
    "ght",
    "ver",
    "ine",
    "ous",
    "rom",
    "ove",
    "ive",
    "sky",
    "tion",
    "that",
    "ould",
    "have",
    "from",
    "with",
    "like",
    "love",
    "live",
    "ever",
    "here",
    "hich",
    "ther",
    "there",
    "where",
    "which",
    "happy",
    "under",
    "should",
    "spring",
    "eternal",
    "birds",
    "light",
    "gather",
    "follow",
    "exiled",
    "pollen",
    "season",
    "shines",
    "smiles",
    "never",
    "cannot",
    "golden",
    "roses",
    "blossoms",
    "country",
    "marvelous",
    "orange",
    "softer",
]

WEIGHTS = {w: 3 if len(w) >= 5 else 2 if len(w) >= 4 else 1 for w in SCORE_WORDS}


def score_plaintext(pt):
    """Score a plaintext by counting weighted common English word hits."""
    return sum(pt.count(w) * WEIGHTS[w] for w in SCORE_WORDS)


def main():
    ct = CIPHERTEXT

    groups = ["" for _ in range(KEY_LENGTH)]
    for i, ch in enumerate(ct):
        groups[i % KEY_LENGTH] += ch

    initial_key = "".join(chr(find_key_letter(g) + ord("a")) for g in groups)

    print("=" * 70)
    print("VIGENÈRE KEY REFINEMENT (greedy hill-climbing)")
    print("=" * 70)
    print(f'\n  Initial key from chi-squared: "{initial_key}"')
    print(
        f"  Initial plaintext score: {score_plaintext(decrypt_vigenere(ct, initial_key))}"
    )

    key = list(initial_key)

    for round_num in range(1, 11):
        changed = False
        for pos in range(KEY_LENGTH):
            best_letter = key[pos]
            best_score = -1
            for shift in range(26):
                trial = key[:]
                trial[pos] = chr(shift + ord("a"))
                pt = decrypt_vigenere(ct, "".join(trial))
                s = score_plaintext(pt)
                if s > best_score:
                    best_score = s
                    best_letter = chr(shift + ord("a"))
            if key[pos] != best_letter:
                changed = True
                key[pos] = best_letter
        if not changed:
            break

    refined_key = "".join(key)

    print(f'  Refined key after {round_num} round(s): "{refined_key}"')
    print(
        f"  Refined plaintext score: {score_plaintext(decrypt_vigenere(ct, refined_key))}"
    )

    if refined_key != initial_key:
        print(f"\n  Changes from chi-squared → refined:")
        for i in range(KEY_LENGTH):
            if initial_key[i] != refined_key[i]:
                print(f"    Position {i:2d}: '{initial_key[i]}' → '{refined_key[i]}'")

    plaintext = decrypt_vigenere(ct, refined_key)
    pt_ioc = index_of_coincidence(plaintext)

    print(f"\n{'=' * 70}")
    print(f'DECRYPTED PLAINTEXT  (key = "{refined_key}", IoC = {pt_ioc:.4f})')
    print(f"{'=' * 70}\n")

    for i in range(0, len(plaintext), 70):
        print(f"  {plaintext[i:i+70]}")


if __name__ == "__main__":
    main()
