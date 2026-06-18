# sources/storage-engines/sqlite/tool/enlargedb.c

## Purpose
`enlargedb.c` appends unused pages to an SQLite database by increasing the database-size header field and extending the file with zeros. It intentionally creates databases that fail `PRAGMA integrity_check` because the appended pages are not valid allocated structures, while remaining useful for boundary and file-size tests.

## Important APIs, Types, and Functions
The program is a single `main()` using `strtoll()`, binary file I/O, SQLite header validation, page-size decoding, database page-count field updates at header bytes 28-31, `fseek()`, and `fwrite()`.

## Control Flow
It requires `DATABASE N`, parses `N`, opens the database read/write, reads the first 100 bytes, validates the SQLite signature and page size, reads the current page count, clamps the new count to `0xffffffff`, writes the new count back to the header, seeks to the last byte of the enlarged database, writes one zero byte, and exits.

## State and Persistence
The target database file is modified in place. Header page count and file length change permanently. No journal or SQLite API is used.

## Dependencies and Integration Points
It depends only on the C runtime and SQLite file format knowledge. It integrates with low-level SQLite tests for oversized files, page-count limits, and corruption/integrity behavior.

## Risks
This intentionally corrupts integrity semantics and should only be used on disposable databases. It has limited error checking for `fseek()`/`fwrite()`, uses `long` seek casts that may be non-portable for very large files, and does not coordinate with active SQLite connections.

## Test Signals
Run on a copy of a valid database and verify file size and header page count increase. `PRAGMA integrity_check` should report problems, while basic open/read scenarios may still work depending on access pattern. Invalid signatures, invalid page sizes, missing args, and non-positive `N` should fail.
