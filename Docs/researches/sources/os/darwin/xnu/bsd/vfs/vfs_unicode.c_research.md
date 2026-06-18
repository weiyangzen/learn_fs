# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_unicode.c

Implements XNU UTF-8 normalization, optional case folding, comparison, hashing, UTF-32/UTF-8 conversion, and substring matching for filesystem names and paths using generated Unicode trie data.

Key behavior:
- Reports Unicode normalization/casefold data version `16.0.0` with code revision `0`.
- `utf8_normalizeOptCaseFoldAndHash` streams an input UTF-8 filename into normalized UTF-32 buffers, optionally case-folds, canonical-orders combining marks, rejects NUL and slash, and feeds normalized code units to a caller-supplied hash function.
- `utf8_normalizeOptCaseFoldAndCompare` normalizes two UTF-8 strings in parallel, reorders combining marks independently, compares buffer chunks, supports early non-equal returns, and includes special pushback handling for Greek iota case-folding at buffer boundaries.
- `utf8_normalizeOptCaseFold` converts a UTF-8 string to normalized UTF-32 output, returning `ENOMEM` when the caller buffer cannot hold the result.
- `utf8_normalizeOptCaseFoldToUTF8_internal` normalizes and optionally case-folds, then converts normalized UTF-32 code points back to UTF-8; the public filename variant rejects slash, while the path variant allows slash but still rejects NUL.
- `utf8_normalizeOptCaseFoldAndMatchSubstring` searches for an already-normalized UTF-32 substring inside a UTF-8 source after on-demand normalization into caller-provided workspace, avoiding normalization when the substring is clearly too long.
- `nextBaseAndAnyMarks` is the shared streaming engine: it decodes ASCII fast paths, validates illegal ASCII characters, decodes non-ASCII UTF-8, normalizes/case-folds each code point, accumulates a base plus following combining marks, enforces stream-safe buffer limits, and flags when canonical reordering is needed.
- `doReorder` performs simple combining-class bubble sort with `swapBufCharCCWithPrevious`.
- `u32CharToUTF8Bytes` encodes valid Unicode code points into one to four UTF-8 bytes.
- `utf8ToU32Code` validates and decodes UTF-8 sequences using ICU-derived lead/trail logic, rejects overlong forms, malformed trails, surrogate mappings, out-of-range code points, and illegal lead-byte lengths.
- `normalizeOptCaseFoldU32Char` maps one UTF-32 code point through generated normalization/case-fold trie tables, rejects unassigned/invalid/noncharacter ranges, handles high private-use area, algorithmic Hangul decomposition, direct combining-class flags, invalid masks, UTF-16/UTF-32 decomposition sequence tables, and case-fold-only mappings.
- `adjustCase` applies simple case folding and the U+0345-to-U+03B9 special case when case-insensitive behavior is requested.
- `getCombClassU32Char` retrieves combining classes for decomposition expansion tail characters, including special treatment for U+03B9 as folded U+0345.
- `decomposeHangul` decomposes precomposed Hangul syllables into leading, vowel, and optional trailing Jamo code points.

Dependencies:
- Includes `sys/unicode.h` and generated `vfs_unicode_data.h` tables such as `nfTrieHi`, `nfTrieMid`, `nfTrieLo`, sequence tables, invalid masks, and simple case-fold tables.
- Logic is adapted from ICU UTF-8 and normalization behavior but implemented as kernel-local code with fixed stack buffers.

Research notes:
- The exported APIs are streaming and allocation-free from the caller perspective; callers provide hash callbacks, output buffers, or working memory.
- Filename-oriented functions reject `/`, while the explicit path normalization variant allows it. All variants reject embedded NUL.
- Error behavior can be intentionally partial: compare and substring APIs may return a definitive unequal/match result before later invalid bytes would have been decoded.
