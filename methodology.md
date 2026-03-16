# Vigenère Cipher Cryptanalysis — Methodology

## Overview

The Vigenère cipher encrypts plaintext by shifting each letter by a different amount, determined by a repeating keyword. To crack it without knowing the key, we follow a three-stage pipeline:

1. **Determine the key length** (Kasiski Examination + Index of Coincidence)
2. **Determine each key letter** (Chi-squared frequency analysis)
3. **Refine the key** (Greedy hill-climbing with English word scoring)

---

## Stage 1: Determining the Key Length

### 1a — Index of Coincidence (IoC)

The Index of Coincidence measures how likely it is that two randomly chosen letters from a text are the same. It is defined as:

$$IC = \frac{\sum_{i=0}^{25} n_i (n_i - 1)}{N(N - 1)}$$

where $n_i$ is the count of the $i$-th letter and $N$ is the total length.

- **English text** has an IoC of approximately **0.065** (letters are unevenly distributed — e, t, a are common).
- **Random/uniformly distributed text** has an IoC of approximately **0.038** (all letters equally likely).

**How we use it:** For each candidate key length $m$ (1 through 20), we split the ciphertext into $m$ groups, where group $k$ contains every $m$-th character starting at position $k$. If $m$ is the correct key length, each group was encrypted with the same single Caesar shift, so its letter distribution should resemble English. We compute the IoC of each group and take the average.

The candidate key length with the **highest average IoC** (closest to 0.065) is most likely correct.

**Our result:** Key length **14** had the highest average IoC at **0.052**. While lower than the ideal 0.065 (due to the short ciphertext of only 390 characters, giving ~28 characters per group), it was clearly the strongest candidate.

### 1b — Kasiski Examination

The Kasiski examination looks for **repeated sequences** (trigrams, 4-grams, 5-grams) in the ciphertext. If the same plaintext fragment is encrypted at two positions that are both aligned to the same key offset, the ciphertext will repeat as well. The **distance** between these repetitions must be a multiple of the key length.

**Procedure:**
1. Scan the ciphertext for all repeated sequences of length 3, 4, and 5.
2. Record the distance between each pair of occurrences.
3. For each candidate factor (2 through 20), count how many distances are divisible by that factor.
4. The factor that divides the most distances is a strong candidate for the key length.

**Our result:** Factors **2**, **7**, and **14** all appeared frequently (10, 9, and 9 times respectively). Since 14 = 2 × 7, this is consistent — all distances divisible by 14 are also divisible by 2 and 7. Combined with the IoC result, we selected **key length 14**.

---

## Stage 2: Determining Each Key Letter (Chi-Squared Analysis)

Once we know the key length $m = 14$, we split the ciphertext into 14 groups. Each group was encrypted with a single Caesar shift (one letter of the key). To find that shift, we use the **chi-squared statistic**.

### Chi-squared ($\chi^2$) test

For each of the 26 possible shifts (a=0, b=1, ..., z=25), we decrypt the group and compare its letter frequencies to standard English frequencies:

$$\chi^2 = \sum_{i=0}^{25} \frac{(O_i - E_i)^2}{E_i}$$

where $O_i$ is the observed count of the $i$-th letter and $E_i = N \times f_i$ is the expected count based on English frequency $f_i$.

The shift with the **lowest $\chi^2$ value** best matches English and is selected as the key letter for that position.

**Our result:** This produced the initial key **`"ipethomesgzbro"`**. The decrypted text contained recognizable English fragments ("and", "the", "which", "happy", "shore") but also significant garbled sections, indicating some key letters were incorrect due to the small sample size (~28 characters per group).

---

## Stage 3: Greedy Hill-Climbing Refinement

The chi-squared method analyzes each key position **independently**, using only ~28 characters per group. With such small samples, statistical noise can cause incorrect letter choices. The refinement step corrects this by evaluating key changes against the **full plaintext**.

### Procedure

1. Start with the chi-squared key (`"ipethomesgzbro"`).
2. For each key position (0 through 13):
   - Try replacing that position's letter with each of the 26 possibilities (a–z).
   - For each candidate, decrypt the **entire** ciphertext.
   - Score the resulting plaintext by counting occurrences of common English words and fragments (e.g., "the", "and", "where", "should", "eternal", "spring"), weighted by word length (longer words = stronger signal).
   - Keep the letter that produces the highest score.
3. Repeat the full pass until no positions change (convergence).

### Why this works

A single wrong key letter corrupts every 14th character in the plaintext, destroying many English words. Trying all 26 options for one position and scoring the full output detects which letter produces the most coherent English. This is a much stronger signal than frequency analysis on 28 characters alone.

### Scoring function

Words are weighted by length:
- **3-letter words** (the, and, for, but, ...): weight **1**
- **4-letter words** (that, from, with, like, ...): weight **2**
- **5+ letter words** (there, where, should, eternal, spring, ...): weight **3**

This prioritizes longer matches, which are far less likely to occur by chance.

**Our result:** The refinement converged in **2 rounds**, changing 4 key positions:

| Position | Chi-squared | Refined |
|----------|-------------|---------|
| 1        | p           | s       |
| 7        | e           | a       |
| 9        | g           | a       |
| 10       | z           | m       |

The refined key is **`"isethomasambro"`**, which produces a plaintext score of **185** (up from 34). The decrypted text is clearly readable English for the majority of the output.

---

## Summary of Results

| Stage | Key | Plaintext Quality |
|-------|-----|-------------------|
| Chi-squared only | `ipethomesgzbro` | Partially readable, many garbled sections |
| After refinement | `isethomasambro` | Mostly readable English |

### Decrypted text (key = `isethomasambro`)

The plaintext (with spaces added for readability):

> [garbled first ~95 chars] ...softer and birds lighter where bees gather pollen in every season and where shines and smiles like a gift from god an eternal springtime under a never blue sky alas but i cannot follow you to that happy shore from which fate has exiled me there it is there that i should like to live to love to love and to die it is there that i should like to live it is there yes there

The text is an English prose translation of Goethe's *Mignon's Song* ("Kennst du das Land"), famously set to music by the French composer **Ambroise Thomas** in his opera *Mignon* — which is consistent with the key containing the letters of "ambroisethomas" (a rotation of our recovered key).

### Note on the garbled first section

The first ~95 characters of the decrypted output appear garbled despite the rest being clear English. Analysis revealed that the ciphertext provided was missing 5 characters at position 95, causing a key alignment shift partway through the text. With the corrected (395-character) ciphertext, the key `"ambroisethomas"` decrypts the entire text flawlessly.
