# File Research: sources/local-fs/apfs-fuse/ApfsLib/Unicode.cpp

This file implements APFS-oriented Unicode normalization and optional case folding. It consumes generated lookup tables from `UnicodeTables_v10.h` and exposes routines used by filename hashing and normalized filename comparison.

`normalizeJimdo()` handles Hangul syllable decomposition algorithmically. Given a precomposed Hangul syllable, it emits leading consonant, vowel, and optional trailing consonant Jamo with canonical combining class zero.

`normalizeOptFoldU32Char()` is the core per-character normalization/folding routine. It rejects invalid/sentinel code points, maps supported Unicode ranges into table indices, looks up high/mid/low trie entries, handles direct identity/combining-class results, Hangul decomposition, invalid masks, two- and three-code-unit sequences, miscellaneous variable-length UTF-16 sequences, UTF-32 single mappings, and UTF-32 variable sequences. When case folding is enabled, it applies `nf_basic_cf` for code points below `0x500` and maps final combining Greek ypogegrammeni `0x345` to iota.

`CanonicalReorder()` reorders decomposed sequences by canonical combining class, preserving starter boundaries. It performs a local bubble-sort-like pass over adjacent nonzero combining-class ranges.

`NormalizeFoldString()` converts a vector of UTF-32 input characters into normalized decomposed output, optionally case-folded. It preallocates up to four output code points per input character, calls `normalizeOptFoldU32Char()` for each character, rejects invalid mappings, trims the output, and performs canonical reordering.

Important behavior: the normalization function returns false only when a character maps to `-1`; some unsupported sequence lengths return zero and effectively drop the character from output. Consumers should be aware that this is a custom APFS-matching normalization path rather than a general-purpose Unicode library.
