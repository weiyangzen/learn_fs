# File Research: sources/os/linux/linux-stable/fs/unicode/utf8-norm.c

## Summary
Implements the UTF-8 trie decoder and normalization cursor used by kernel Unicode normalization and casefolding.

## Key APIs
- `utf8version_is_supported()`
- `utf8nlen()`
- `utf8ncursor()`
- `utf8byte()`

## Important Behavior
The file decodes a compact generated trie. Internal node bytes encode bit tests, optional next-byte advancement, relative right-node offsets, and node/leaf markers. Leaves contain Unicode generation, canonical combining class, and optional decomposition string.

`utf8nlookup()` validates UTF-8 by walking the trie and returns a leaf only for well-formed Unicode scalar values known to the generated table. Surrogates and invalid encodings are excluded by construction.

Hangul syllables are decomposed algorithmically when a leaf contains the special `HANGUL` marker. The synthesized leaf emits L, V, and optional T jamo sequences.

`utf8nlen()` computes the byte length of the normalized form without producing it. Characters newer than the selected table version pass through with their original byte length; decomposable characters use decomposition length.

`utf8ncursor()` initializes a normalization cursor and rejects NULL strings, length truncation overflow, and inputs beginning with a UTF-8 continuation byte.

`utf8byte()` streams one normalized byte at a time. It expands decomposition strings, skips empty decompositions for default ignorables, treats too-new characters as stoppers, and performs canonical combining class ordering by repeated scans between stopper characters.

## Dependencies
Consumes `struct unicode_map`, generated `utf8data` tables, `enum utf8_normalization`, and internal declarations from `utf8n.h`.

## Risks
Runtime trie decoding must stay byte-for-byte compatible with `mkutf8data.c` emission. The cursor intentionally rescans combining runs, so malformed trie data or invalid leaves would affect normalization ordering and validation. Callers must handle `-1` from `utf8byte()` as invalid input.
