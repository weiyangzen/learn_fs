# File Research: sources/os/linux/linux-stable/fs/hfsplus/unicode.c

## Role

Implements HFS+ Unicode string comparison, case folding, Unicode-to-local-NLS conversion, local-NLS-to-HFS+ Unicode conversion, canonical decomposition/composition, Linux/HFS+ filename character compatibility mapping, dentry hashing, and dentry comparison.

## Case-Sensitive and Case-Insensitive Comparisons

- `case_fold(u16 c)`
  - Uses `hfsplus_case_fold_table`.
  - Returns folded value, original value if no subtable exists, or zero for ignorable characters.
- `hfsplus_strcasecmp()`
  - Reads big-endian HFS+ Unicode string lengths.
  - Clamps invalid lengths above `HFSPLUS_MAX_STRLEN` and logs correction.
  - Case-folds each code unit, skipping ignorables mapped to zero.
  - Returns normal strcmp-style ordering.
- `hfsplus_strcmp()`
  - Case-sensitive 16-bit code-unit comparison.
  - Also clamps invalid lengths above `HFSPLUS_MAX_STRLEN`.
  - Orders by first differing code unit, then length.

These functions are exported to KUnit with `EXPORT_SYMBOL_IF_KUNIT`.

## Composition and Decomposition

- Hangul constants implement Unicode algorithmic Hangul composition/decomposition.
- `hfsplus_compose_lookup()`
  - Binary-searches composition table entries and returns a continuation table or result pointer.
- `hfsplus_decompose_nonhangul()`
  - Walks the nibble-indexed `hfsplus_decompose_table`.
  - Extracts decomposition size from low two bits of the final encoded offset.
- `hfsplus_try_decompose_hangul()`
  - Implements Unicode Annex #15 Hangul decomposition into L/V/T jamo.
- `decompose_unichar()`
  - Uses Hangul algorithm first, then table-based non-Hangul decomposition.

## HFS+/Linux Compatibility Mapping

HFS+ permits characters that Linux path components cannot represent directly:

- Mac-to-Linux conversion:
  - HFS+ NUL `0x0000` maps to Unicode `0x2400`.
  - HFS+ slash `/` maps to Linux colon `:`.
- Linux-to-Mac conversion:
  - Unicode `0x2400` maps back to NUL.
  - Linux colon `:` maps back to HFS+ slash `/`.
- Xattr names bypass these conversions (`HFS_XATTR_NAME`).

## Unicode to Local Name Conversion

- `hfsplus_uni2asc()`
  - Converts HFS+ Unicode strings to local NLS bytes.
  - Clamps source length to max name length.
  - Composes decomposed HFS+ sequences unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Handles Hangul composition.
  - Applies Mac-to-Linux compatibility mapping for regular names.
  - Uses `nls->uni2char()`, replacing unsupported characters with `?` except for `-ENAMETOOLONG`.
  - Returns output byte length through `len_p`.
- `hfsplus_uni2asc_str()` wraps regular filename conversion with `HFSPLUS_MAX_STRLEN`.
- `hfsplus_uni2asc_xattr_str()` wraps xattr-name conversion with `HFSPLUS_ATTR_MAX_STRLEN`.

## Local Name to HFS+ Unicode Conversion

- `asc2unichar()`
  - Uses `nls->char2uni()`.
  - Replaces conversion failures with `?`.
  - Applies Linux-to-Mac compatibility mapping.
- `hfsplus_asc2uni()`
  - Converts local bytes to HFS+ Unicode.
  - Decomposes characters unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Uses Hangul algorithm and decomposition table.
  - Stops at `max_unistr_len`, writes output length, and returns `-ENAMETOOLONG` if source bytes remain.

## Dentry Hash and Compare

- `hfsplus_hash_dentry()`
  - Converts a Linux qstr through NLS and compatibility mapping.
  - Optionally decomposes codepoints.
  - Optionally case-folds when `HFSPLUS_SB_CASEFOLD` is set.
  - Skips casefold-ignorable zero results.
  - Produces Linux dcache hash via `partial_name_hash()` / `end_name_hash()`.
- `hfsplus_compare_dentry()`
  - Converts both names through the same pipeline.
  - Maintains decomposition iterators for both sides.
  - Applies case folding and skips ignorable folded characters.
  - Returns strcmp-style ordering and length ordering.

## Dependencies

Uses NLS callbacks, KUnit visibility exports, HFS+ Unicode tables, mount flags, and Linux dentry string-hash helpers.

## Research Notes

The `HFSPLUS_SB_NODECOMPOSE` flag is inverted relative to a simple `decompose` boolean: when the bit is clear, conversion/hash/compare decompose or compose as needed; when the bit is set, nodecompose behavior preserves non-decomposed form. This file is also where HFS+’s colon/slash mismatch is normalized for Linux pathnames. Xattr names intentionally skip that mapping.
