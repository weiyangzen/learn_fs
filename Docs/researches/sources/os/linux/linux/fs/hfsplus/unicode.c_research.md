# File Research: sources/os/linux/linux/fs/hfsplus/unicode.c

## Role

Implements HFS+ Unicode string comparison, case folding, Linux/HFS+ filename character compatibility conversions, Unicode composition/decomposition, conversion between HFS+ Unicode names and Linux byte strings through NLS, and dentry hash/compare hooks.

## Case-Sensitive and Case-Insensitive Comparison

- `case_fold(u16 c)`
  - Looks up a character through `hfsplus_case_fold_table`.
  - Returns folded character, original character when no subtable exists, or zero for ignorable characters.
- `hfsplus_strcasecmp()`
  - Compares `hfsplus_unistr` values after case folding.
  - Clamps corrupt lengths greater than `HFSPLUS_MAX_STRLEN` and logs correction.
  - Skips case-folded zero/ignorable characters.
  - Returns strcmp-like `-1`, `0`, or `1`.
- `hfsplus_strcmp()`
  - Compares `hfsplus_unistr` values as unsigned 16-bit code units.
  - Also clamps overlong lengths and logs correction.
  - Returns lexicographic order with length as tiebreaker.

The string comparison functions are exported under `EXPORT_SYMBOL_IF_KUNIT` for KUnit tests.

## Composition and Decomposition

- Hangul constants implement Unicode decomposition/composition ranges.
- `hfsplus_compose_lookup()` binary-searches nested composition records in `hfsplus_compose_table`.
- `hfsplus_decompose_nonhangul()` walks `hfsplus_decompose_table` levels by nibbles to find non-Hangul decomposition sequences.
- `hfsplus_try_decompose_hangul()` implements Unicode Annex #15 Hangul decomposition into L/V/T jamo.
- `decompose_unichar()` tries Hangul first, then non-Hangul table decomposition.

## Linux/HFS+ Character Compatibility

HFS+ permits characters that conflict with Linux path/string conventions:

- `hfsplus_mac2linux_compatibility_check()` maps HFS+ NUL to U+2400 and HFS+ slash (`/`) to Linux colon (`:`) for regular names. It bypasses this conversion for xattr names.
- `hfsplus_linux2mac_compatibility_check()` maps Linux U+2400 back to NUL and Linux colon back to HFS+ slash for regular names. It bypasses this conversion for xattr names.
- `asc2unichar()` converts one Linux byte sequence to a Unicode character through the mount NLS table, substitutes `?` on conversion failure, then applies Linux-to-HFS+ compatibility mapping.

## Name Conversion

- `hfsplus_uni2asc()`
  - Converts HFS+ Unicode names to Linux byte strings.
  - Uses the mount NLS `uni2char` callback.
  - Clamps overlong HFS+ string lengths to the supplied maximum.
  - Composes decomposed sequences unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Special-cases Hangul composition.
  - Converts HFS+ slash/NUL for regular names.
  - Returns `-ENAMETOOLONG` when the output buffer is too small; otherwise substitutes `?` for conversion failures.
- `hfsplus_uni2asc_str()` converts normal HFS+ strings with `HFSPLUS_MAX_STRLEN`.
- `hfsplus_uni2asc_xattr_str()` converts attribute strings with `HFSPLUS_ATTR_MAX_STRLEN` and xattr-name conversion rules.
- `hfsplus_asc2uni()`
  - Converts Linux byte strings to HFS+ Unicode strings through the mount NLS `char2uni` callback.
  - Decomposes characters unless `HFSPLUS_SB_NODECOMPOSE` is set.
  - Handles Hangul and table-driven non-Hangul decomposition.
  - Stops at `max_unistr_len` and returns `-ENAMETOOLONG` if input remains.

## Dentry Hooks

- `hfsplus_hash_dentry()`
  - Converts each byte sequence to Unicode, applies Linux-to-HFS+ compatibility mapping, optionally decomposes, optionally casefolds, skips ignorable folded characters, and feeds 16-bit values into Linux name hashing.
  - Writes the final hash into `str->hash`.
- `hfsplus_compare_dentry()`
  - Converts both names to Unicode streams, optionally decomposes and casefolds each side, skips ignorable folded characters, and returns lexicographic order.
  - Uses remaining byte lengths as the final tiebreaker.

Both dentry hooks are exported for KUnit visibility.

## Dependencies

Uses NLS conversion callbacks, Linux dentry/string hashing helpers, KUnit visibility export macros, HFS+ raw constants, and the three Unicode tables from `tables.c`.

## Research Notes

The Unicode implementation is central to correctness for catalog lookup and Linux dcache behavior. HFS+ filenames are stored in a historical decomposed form and may be case-sensitive or case-insensitive depending on volume flags. The `nodecompose` flag inverts the default conversion behavior: without it, Linux-facing conversion tries to compose decomposed names; with it, node names remain decomposed.
