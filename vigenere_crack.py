from collections import Counter
from math import gcd
from functools import reduce

with open("cypher.txt") as f:
    CIPHERTEXT = f.read().strip()

# taken from wikipedia: https://en.wikipedia.org/wiki/Letter_frequency
ENGLISH_FREQ = [
    0.08167,
    0.01492,
    0.02782,
    0.04253,
    0.12702,
    0.02228,
    0.02015,
    0.06094,
    0.06966,
    0.00153,
    0.00772,
    0.04025,
    0.02406,
    0.06749,
    0.07507,
    0.01929,
    0.00095,
    0.05987,
    0.06327,
    0.09056,
    0.02758,
    0.00978,
    0.02360,
    0.00150,
    0.01974,
    0.00074,
]


def index_of_coincidence(text):
    n = len(text)
    counts = Counter(text)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1))


def average_ioc(ciphertext, key_length):
    groups = ["" for _ in range(key_length)]
    for i, ch in enumerate(ciphertext):
        groups[i % key_length] += ch
    iocs = [index_of_coincidence(g) for g in groups]
    return sum(iocs) / len(iocs)


def kasiski_examination(ciphertext):
    sequences = {}
    for seq_len in range(3, 6):  # look at sequences from 3 letters to 5 letters in len
        for i in range(len(ciphertext) - seq_len + 1):
            seq = ciphertext[i : i + seq_len]
            # add all positions that the same sequence occurs at
            sequences.setdefault(seq, []).append(i)

    repeated = {
        seq: positions for seq, positions in sequences.items() if len(positions) > 1
    }

    distances = []
    for positions in repeated.values():
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                distances.append(positions[j] - positions[i])

    overall_gcd = reduce(gcd, distances) if distances else 0
    return repeated, distances, overall_gcd


def chi_squared(observed_counts, n, expected_freq):
    """Chi-squared statistic comparing observed counts to expected English."""
    return sum(
        (observed_counts.get(chr(ord("a") + i), 0) - n * expected_freq[i]) ** 2
        / (n * expected_freq[i])
        for i in range(26)
    )


def find_key_letter(group):
    """Try all 26 shifts on a group and return the shift with lowest chi²."""
    n = len(group)
    best_shift, best_score = 0, float("inf")
    for shift in range(26):
        decrypted = "".join(
            chr((ord(ch) - ord("a") - shift) % 26 + ord("a")) for ch in group
        )
        counts = Counter(decrypted)
        score = chi_squared(counts, n, ENGLISH_FREQ)
        if score < best_score:
            best_score = score
            best_shift = shift
    return best_shift


def decrypt_vigenere(ciphertext, key):
    """Decrypt ciphertext with the given key."""
    m = len(key)
    key_shifts = [ord(k) - ord("a") for k in key]
    return "".join(
        chr((ord(c) - ord("a") - key_shifts[i % m]) % 26 + ord("a"))
        for i, c in enumerate(ciphertext)
    )


def main():
    ciphertext = CIPHERTEXT
    print(f"\nCiphertext len: {len(ciphertext)}\n")

    print("Step 1: calculate avg index of coincidende\n")

    # wikipedia says english IoC is 1.73, which when dvidied by number of letters
    # we get ~0.67. As close to that value as we can get would be best.
    # https://en.wikipedia.org/wiki/Index_of_coincidence
    print("\nCalculate average index of coincidende:\n")

    ioc_results = {}
    for m in range(1, 21):  # assume key not larger than 20
        avg = average_ioc(ciphertext, m)
        ioc_results[m] = avg
        print(f"{m}:\t\t{avg:.5f}")

    best_ioc_length = max(ioc_results, key=lambda k: ioc_results[k])
    print(
        f"\nBest candidate by IoC: key length = {best_ioc_length} "
        f"(avg IoC = {ioc_results[best_ioc_length]})"
    )

    print("\nStep 2: Kasiski Examination\n")

    _, _, overall_gcd = kasiski_examination(ciphertext)

    # displaying this didn't help much

    # find top 15 repeated sequences
    # top_15_repeated = sorted(repeated.items(), key=lambda x: -len(x[1]))[:15]
    # print(f"\n  Top 15 repeated sequences (sequence | count | positions):\n")
    # for seq, positions in top_15_repeated:
    #     dists = [
    #         positions[j] - positions[i]
    #         for i in range(len(positions))
    #         for j in range(i + 1, len(positions))
    #     ]
    #     print(f"  {seq:<10} {len(positions):>5}  pos={positions}  dists={dists}")

    print(f"\nGCD of all distances: {overall_gcd}")

    print("\nStep 3: Chi-squared")
    print("Pick the key length whose output is most readable.\n")
    # none turn out to be readable, just take 14 as it has the highest score

    for key_length in range(1, 21):
        groups = ["" for _ in range(key_length)]
        for i, ch in enumerate(ciphertext):
            groups[i % key_length] += ch

        key = ""
        for group in groups:
            shift = find_key_letter(group)
            key += chr(shift + ord("a"))

        plaintext = decrypt_vigenere(ciphertext, key)
        avg_ioc = ioc_results[key_length]
        pt_ioc = index_of_coincidence(plaintext)

        print(f'\nKey length: {key_length}  |  Key: "{key}"')
        print(f"Avg group IoC: {avg_ioc:.5f}  |  Plaintext IoC: {pt_ioc:.5f}\n")
        for i in range(0, len(plaintext), 70):
            print(f"  {plaintext[i:i+70]}")


if __name__ == "__main__":
    main()
