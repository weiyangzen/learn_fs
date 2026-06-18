# sources/storage-engines/sqlite/tool/extract.c

## Purpose
`extract.c` copies a byte range from a file to stdout. It is a minimal helper for constructing binary fixtures or isolating sections of database files.

## Important APIs, Types, and Functions
The program consists of `main()` using `fopen()`, `atoi()`, `malloc()`, `fseek()`, `fread()`, `fclose()`, and `fwrite()`.

## Control Flow
It requires `FILENAME OFFSET AMOUNT`, opens the file in binary mode, allocates `AMOUNT` bytes, seeks to `OFFSET`, reads the requested amount, and writes it to stdout if the full read succeeds. Errors print to stderr and return non-zero.

## State and Persistence
It does not modify input files. Output is raw binary on stdout. Heap state is not explicitly freed before process exit.

## Dependencies and Integration Points
Only the C runtime is required. The tool can be used by SQLite scripts that need deterministic byte slices from database files.

## Risks
`atoi()` provides weak validation and cannot report overflow or negative values cleanly. Negative or very large amounts can lead to bad allocations or undefined behavior through conversion to `size_t`. `fseek()` status is not checked. The diagnostic for short reads prints `size_t` with `%d`, which is type-incorrect.

## Test Signals
Test exact extraction, offset past EOF, short reads, zero amount, negative arguments, binary data containing NUL bytes, and stdout redirection.
