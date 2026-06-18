# File Research: sources/os/linux/linux/fs/unicode/utf8-core.c

## Purpose
Provides exported kernel Unicode APIs for UTF-8 validation, normalized comparison, casefolding, hashing, normalization, table loading/unloading, and version parsing.

## Main Contents
- Validation and comparisons:
  - `utf8_validate()` checks whether a `qstr` is valid under NFDI traversal.
  - `utf8_strncmp()` compares two strings after NFDI normalization.
  - `utf8_strncasecmp()` compares two strings after NFDICF normalization.
  - `utf8_strncasecmp_folded()` compares a pre-folded string against the NFDICF form of another string.
- Transformation helpers:
  - `utf8_casefold()` writes NFDICF output into a destination buffer.
  - `utf8_normalize()` writes NFDI output into a destination buffer.
  - `utf8_casefold_hash()` hashes the NFDICF byte stream using Linux name-hash helpers.
- Table/version handling:
  - `find_table_version()` selects the table entry matching a requested Unicode version.
  - `utf8_load()` allocates `struct unicode_map`, requests `utf8_data_table`, checks version support, and sets NFDI/NFDICF table pointers.
  - `utf8_unload()` releases the data-table symbol and map.
  - `utf8_parse_version()` parses `MAJ.MIN.REV` into `UNICODE_AGE()` format.
- Exports all public functions with `EXPORT_SYMBOL`.

## Important Design Points
- API comparison returns `0` for equal, `1` for unequal, and `-EINVAL` for invalid UTF-8 or cursor errors.
- Transform functions require enough destination space for the terminating NUL; otherwise they return `-EINVAL`.
- `utf8_casefold_hash()` hashes normalized bytes without materializing a separate folded string.
- `utf8_load()` uses `symbol_request(utf8_data_table)` so the large table can be modular.

## Cross-File Relationships
- Includes `utf8n.h`.
- Calls cursor and normalization length functions implemented in `utf8-norm.c`.
- Consumes generated `utf8_data_table` from `utf8data.c`.
- Uses public `struct unicode_map` and normalization enum from `linux/unicode.h`.

## Risks / Review Notes
- `utf8_strncasecmp_folded()` assumes `cf` is already valid UTF-8 casefolded data and indexes it until the normalized cursor ends; caller must ensure `cf` is NUL-terminated/long enough.
- `find_table_version()` starts at the last entry and decrements while `version < maxage`; malformed empty tables would underflow, though generated tables are expected valid.
- `utf8_parse_version()` returns `int` even though `UNICODE_AGE()` is unsigned-style packed; invalid negative parser inputs are rejected by `match_int()` failure or packing behavior checks elsewhere.
