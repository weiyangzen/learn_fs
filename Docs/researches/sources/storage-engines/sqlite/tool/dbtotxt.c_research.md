# sources/storage-engines/sqlite/tool/dbtotxt.c

## Purpose
`dbtotxt.c` converts a binary SQLite database or raw file into a compact textual hex dump, suppressing all-zero 16-byte lines. The output is designed for human-readable test fixtures and can optionally include `.open --hexdb` headers for the SQLite CLI.

## Important APIs, Types, and Functions
`allZero()` detects zero-filled 16-byte lines. `main()` parses `--for-cli`, `--script`, `--pagesize N`, and `--raw`, loads the whole file, derives page size from the SQLite header unless overridden or raw, prints page/offset records, hex bytes, safe ASCII rendering, and an end marker.

## Control Flow
The utility validates arguments, reads the full file into memory with 16 bytes of zero padding, optionally splits a zero-terminated SQL prefix from `--script`, validates SQLite minimum size and page size unless raw, derives the basename, prints optional `.open --hexdb`, then loops in 16-byte increments skipping zero lines and printing page headers when the page number changes. If a SQL prefix was present, it prints that script after the hex database.

## State and Persistence
It has no persistent output except stdout redirection chosen by the caller. It reads the entire input into heap memory and frees it before exit.

## Dependencies and Integration Points
Dependencies are only C runtime headers. It integrates with SQLite CLI hex database workflows, test data minimization, and fixture generation.

## Risks
The entire input file is loaded into memory, so very large databases can exhaust memory. `ftell()` and `long` limit portability for huge files. The `--script` prefix expects a zero terminator. Without `--raw`, files shorter than 100 bytes or with invalid page sizes are rejected. It suppresses zero lines, so consumers must understand the custom format.

## Test Signals
Round-trip a small SQLite database through CLI hex import, check `--for-cli` and `--script` headers, verify invalid page sizes fail, compare `--raw` handling of short files, and confirm zero-filled pages are compacted.
