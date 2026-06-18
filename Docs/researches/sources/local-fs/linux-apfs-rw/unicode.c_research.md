# File Research: sources/local-fs/linux-apfs-rw/unicode.c

This file implements APFS filename Unicode normalization and optional case folding for the Linux APFS read-write driver. It is used by catalog key comparison, filename hashing/key generation, and directory/name lookup paths that need APFS-style normalized Unicode semantics.

Public API:
- `apfs_init_unicursor(struct apfs_unicursor *cursor, const char *utf8str, unsigned int total_len)` initializes cursor state over a UTF-8 byte string.
- `apfs_normalize_next(struct apfs_unicursor *cursor, bool case_fold)` returns one normalized UTF-32 codepoint at a time, with optional case folding.

Core implementation:
- `apfs_trie_find()` is a shared lookup helper for three static Unicode data tries. For NFD and case-folding tries it returns a position and length into a value array; for canonical combining class lookup it returns the CCC value directly.
- `apfs_is_precomposed_hangul()` and `apfs_decompose_hangul()` implement algorithmic Hangul syllable decomposition using Unicode 9.0 constants.
- `apfs_normalize_char()` decomposes one UTF-32 codepoint into NFD form and then applies case folding if requested. Characters absent from the lookup tables normalize to themselves.
- `apfs_get_normalization_length()` scans forward from the current UTF-8 position until the next starter after a combining sequence, counting the number of normalized codepoints in that segment.
- `apfs_normalize_next()` emits normalized codepoints in canonical combining class order. For ASCII it has a fast path using `tolower()` when case folding is requested; for non-ASCII it computes a segment length, repeatedly scans the segment, and selects the next codepoint by CCC and position.

Static data:
- `apfs_nfd_trie` plus `apfs_nfd` encode Unicode 9.0 canonical decomposition data.
- `apfs_cf_trie` plus `apfs_cf` encode Unicode 9.0 case-fold mappings.
- `apfs_ccc_trie` encodes canonical combining class values.
- The data tables occupy most of the file and are generated/static Unicode reference data rather than driver control logic.

Integration points:
- `namei.c` uses the cursor to build normalized names for lookup.
- `key.c` uses it for APFS name comparison and key construction.
- The header contract is declared in `unicode.h`.

Important behavior and edge cases:
- Invalid UTF-8 makes normalization return `0`, which is also the end/invalid sentinel for callers.
- Normalization is segment-based: it reorders combining marks only within the substring ending before the next starter.
- The ASCII fast path checks `*utf8str` before checking `total_len`; current callers appear to provide real string storage, but this is a boundary assumption worth preserving if call sites change.
- Embedded NUL bytes terminate normalization because the scanner checks `!*utf8str`, even though a separate byte length is also tracked.

Testing signals:
- High-value tests would cover APFS name comparison for composed/decomposed Latin characters, Hangul syllables, combining mark reordering, invalid UTF-8, ASCII case-folding, and embedded NUL behavior.
