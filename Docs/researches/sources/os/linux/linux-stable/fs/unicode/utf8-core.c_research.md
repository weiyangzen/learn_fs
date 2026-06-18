# File Research: sources/os/linux/linux-stable/fs/unicode/utf8-core.c

## Summary
Provides exported kernel APIs for UTF-8 validation, normalized comparison, casefolding, normalized hashing, normalization output, Unicode table loading/unloading, and version parsing.

## Key APIs
- `utf8_validate()`
- `utf8_strncmp()`
- `utf8_strncasecmp()`
- `utf8_strncasecmp_folded()`
- `utf8_casefold()`
- `utf8_casefold_hash()`
- `utf8_normalize()`
- `utf8_load()`
- `utf8_unload()`
- `utf8_parse_version()`

## Important Behavior
Validation calls `utf8nlen()` in `UTF8_NFDI` mode and returns failure for invalid UTF-8.

Comparisons create `utf8cursor` instances and compare normalized byte streams. Case-insensitive comparisons use `UTF8_NFDICF`; case-sensitive normalized comparisons use `UTF8_NFDI`.

`utf8_casefold()` and `utf8_normalize()` stream normalized bytes into a caller buffer and return the output length excluding the terminating NUL. They return `-EINVAL` if the buffer is too small or input is invalid.

`utf8_casefold_hash()` hashes the NFDI+casefold byte stream with VFS name-hash helpers and writes `qstr.hash`.

`utf8_load()` allocates a `unicode_map`, requests the `utf8_data_table` symbol, validates requested Unicode version support, and selects the appropriate NFDI/NFDICF table entries. `utf8_unload()` releases the symbol and map.

`utf8_parse_version()` accepts strings of the form `major.minor.revision` and returns packed `UNICODE_AGE()` values.

## Dependencies
Uses generated `utf8_data_table`, trie/cursor functions from `utf8-norm.c`, kernel symbol request/put, string hash helpers, parser helpers, and `struct unicode_map`.

## Risks
Callers must load a supported Unicode version before using normalization APIs. Output functions require enough destination space for the normalized form plus NUL. `utf8_strncasecmp_folded()` assumes its first argument is already valid folded UTF-8.
