# File Research: sources/local-fs/ntfs-3g/libntfs-3g/unistr.c

## Scope

Implements Unicode and filename string handling for libntfs-3g: NTFS UTF-16LE comparisons, case folding and collation, UTF-16LE to/from UTF-8 or locale multibyte conversion, `$UpCase` and lowercase table construction, NTFS filename conversion/freeing, forbidden character/name checks, DOS/Win32 name collapse checks, encoding selection, and optional macOS Unicode normalization.

## API And Behavior

- All NTFS Unicode strings are assumed to be little-endian `ntfschar` values.
- `ntfs_names_are_equal()` compares names by length and then uses either case-sensitive `ntfs_ucsncmp()` or case-insensitive `ntfs_ucsncasecmp()`.
- `ntfs_names_full_collate()` implements NTFS directory collation. In case-sensitive mode it compares primarily by uppercased values and uses original case as a tie-breaker; ignore-case mode compares only uppercased values.
- `ntfs_ucsncmp()`, `ntfs_ucsncasecmp()`, `ntfs_ucsnlen()`, and `ntfs_ucsndup()` provide bounded UTF-16LE comparison, case-insensitive comparison through the volume upcase table, length, and duplication helpers.
- `ntfs_name_upcase()`, `ntfs_name_locase()`, and `ntfs_file_value_upcase()` mutate names in place using upcase/locase tables.
- Internal UTF-16LE to UTF-8 conversion validates and sizes output, handles surrogate pairs, supports optional broken-surrogate/U+FFFE/U+FFFF tolerance via `ALLOW_BROKEN_UNICODE`, limits allocated paths to `PATH_MAX`, and optionally normalizes NTFS names to decomposed UTF-8 on macOS.
- Internal UTF-8 to UTF-16LE conversion sizes output, validates UTF-8 byte sequences, rejects invalid ranges unless broken Unicode is allowed, emits surrogate pairs for code points above U+FFFF, and optionally normalizes input to composed UTF-8 on macOS.
- Public `ntfs_ucstombs()` converts NTFS UTF-16LE to either the internal UTF-8 path or the current locale multibyte encoding via wide-character conversion APIs.
- Public `ntfs_mbstoucs()` converts host strings to NTFS UTF-16LE, using the UTF-8 path by default or locale multibyte conversion when configured.
- `ntfs_uppercase_mbs()` uppercases a UTF-8 string using the NTFS upcase table and re-encodes the result as UTF-8.
- `ntfs_upcase_table_build()` builds the default 65,536-entry NTFS upcase table from Windows XP mappings plus version-gated later Windows mappings.
- `ntfs_upcase_build_default()` allocates and builds the default upcase table.
- `ntfs_locase_table_build()` derives a lowercase table from an upcase table, accepting the known sigma ambiguity by mapping uppercase sigma to U+03C3.
- `ntfs_str2ucs()` converts a C string to an NTFS filename, enforces the 255-character NTFS name limit, and returns `AT_UNNAMED` for NULL or empty names.
- `ntfs_ucsfree()` frees strings from `ntfs_str2ucs()` while preserving the `AT_UNNAMED` sentinel.
- `ntfs_forbidden_chars()` rejects empty names, control characters, Win32-forbidden punctuation, backslash, pipe, and optionally trailing space/dot.
- `ntfs_forbidden_names()` extends character checks with reserved DOS device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1..COM9`, `LPT1..LPT9`) with optional suffixes, using the volume upcase table for case-insensitive matching.
- `ntfs_collapsible_chars()` checks whether a short DOS name and long Win32 name can collapse because they are equal or differ only by case.
- `ntfs_set_char_encoding()` selects UTF-8 by default or tries `setlocale()` for non-UTF-8 encodings; invalid locales fall back to UTF-8.
- macOS-only helpers toggle normalization and use CoreFoundation to normalize UTF-8 to NFC or NFD when enabled.

## State And Dependencies

The file uses a process-global `use_utf8` flag and, on macOS with normalization enabled, a process-global `nfconvert_utf8` flag. It depends on volume upcase/locase tables, `FILE_NAME_ATTR`, `AT_UNNAMED`, `PATH_MAX`, locale/wide-character C library APIs, CoreFoundation on macOS when enabled, endian helpers, NTFS allocation helpers, and logging. Filename validation depends on NTFS volume casing tables for reserved-name comparisons.

## Risks And Invariants

The conversion paths are security-sensitive because malformed UTF-8/UTF-16 names must not create ambiguous or non-round-trippable filenames. `ALLOW_BROKEN_UNICODE` defaults to allowing broken surrogate code units, which improves compatibility with existing malformed NTFS names but weakens strict Unicode validation. Several APIs assume callers provide valid non-NULL inputs except in debug-only checks. `ntfs_upcase_table_build()` assumes a sufficiently large caller buffer. Encoding selection is global, not per-volume or per-thread. macOS normalization can replace or copy output buffers, so caller buffer ownership and length handling must follow the documented API behavior.
