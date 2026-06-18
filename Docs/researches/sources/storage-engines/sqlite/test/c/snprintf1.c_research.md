# sources/storage-engines/sqlite/test/c/snprintf1.c

## Purpose
`snprintf1.c` is a public API regression test for `sqlite3_snprintf()` formatting and buffer-size handling around a fixed floating-point value.

## Important APIs, Types, and Functions
It uses optional `sqlite3_initialize()` for `SQLITE_OMIT_AUTOINIT`, `sqlite3_snprintf()`, and `sqlite3_stricmp()`.

## Control Flow
The program formats `2023.0` with `"%.3f"` into a 32-byte buffer twice, once with a size argument of 17 and once with 16. It prints each output and compares it case-insensitively with `"2023.000"`, returning failure if either differs.

## State and Persistence Behavior
No database or persistent state is used. The test covers stack buffer writes and SQLite formatting logic.

## Dependencies and Integration Points
It exercises SQLite's printf implementation in `printf.c` through the public API, especially floating-point formatting and null-termination under size constraints.

## Risks and Edge Cases
The test is narrow: it checks one value and two buffer sizes that are both comfortably large for the expected string. It does not cover truncation, locale differences, infinities, NaNs, or alternate flags.

## Test Signals
Output lines show the formatted strings. Exit status 0 means both outputs matched `2023.000`; exit status 1 flags formatting or initialization failure.
