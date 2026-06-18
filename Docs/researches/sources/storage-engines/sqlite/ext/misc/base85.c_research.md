# sources/storage-engines/sqlite/ext/misc/base85.c

## Purpose
`base85.c` implements base85 conversion as either a SQLite extension or a standalone utility. As an extension it registers `base85(x)` for BLOB/TEXT conversion and optionally `is_base85(t)` for validation.

## Important APIs, types, and functions
- Base85 classification macros map a custom 85-character ASCII alphabet excluding troublesome punctuation/control characters.
- `toBase85()` encodes 4-byte groups to 5 numerals and 1-3 byte tails to 2-4 numerals, optionally inserting separators.
- `fromBase85()` decodes delimited base85 groups back to bytes.
- `allBase85()` and `is_base85()` validate text when not compiled with `OMIT_BASE85_CHECKER`.
- `base85()` is the SQLite UDF dispatcher; `sqlite3_base85_init()` registers SQL functions.
- Under `BASE85_STANDALONE`, `main()` reads/writes binary files and base85 on standard streams.

## Control flow
As a SQLite function, BLOB input is size-checked, allocated, encoded with newline separators, and returned as text. TEXT input is size-estimated, decoded into a BLOB, and returned. `is_base85()` returns null for null, 1 for text containing only base85 numerals/whitespace, 0 otherwise. Standalone mode parses `-r` or `-w` and streams conversion.

## State and persistence behavior
The extension is stateless apart from per-call allocations. Standalone mode touches the requested file or stdin/stdout only. Encoded data can be concatenated when groups are separated by non-base85 characters.

## Dependencies and integration points
It uses SQLite extension APIs when not standalone, and C stdio/string/assert plus optional `ctype.h`. It exposes shell integration macros `BASE85_INIT` and `BASE85_EXPOSE`.

## Risks and edge cases
- The alphabet is custom and not necessarily compatible with Adobe Ascii85 or other variants.
- Non-base85 characters delimit groups during decoding; this is permissive and can hide malformed dark content unless `is_base85()` or standalone warning checks are used.
- `base85()` is registered `DIRECTONLY`, so indirect schema use is blocked.
- Size estimates must remain conservative relative to SQLite length limits.

## Test signals
Round trips for 0-4 byte boundaries, long data with 80-column separators, invalid delimiter handling, `is_base85(NULL/text/blob)`, standalone `-r`/`-w`, and omitted-checker builds are meaningful.
