# sources/storage-engines/sqlite/ext/misc/csv.c

## Purpose

`csv.c` implements a read-only virtual table module named `csv` for reading CSV content from either a filesystem file (`filename=`) or inline text (`data=`). It can infer columns, use a header row, accept an explicit schema, or use a fixed `columns=N` count.

## Important APIs, types, and functions

`sqlite3_csv_init()` registers `csv`; under `SQLITE_TEST` it also registers `csv_wr`, a faux writable variant whose `xUpdate` returns `SQLITE_READONLY`. `CsvReader` owns file/input-buffer state, field accumulation memory, current line, terminator, and error text. `CsvTable` stores configured filename/data, starting offset after a header, column count, and test flags. `CsvCursor` owns a `CsvReader`, per-column value buffers, lengths, and rowid.

Core parsing lives in `csv_read_one_field()`, with buffering in `csv_getc()`, `csv_getc_refill()`, `csv_append()`, and `csv_resize_and_append()`. Parameter parsing is handled by `csv_parameter()`, `csv_string_parameter()`, `csv_boolean_parameter()`, `csv_trim_whitespace()`, and `csv_dequote()`.

## Control flow

`csvtabConnect()` parses module arguments, rejects missing or simultaneous `filename=` and `data=`, optionally opens the input to count columns or read header names, builds a default `CREATE TABLE x(...)` declaration when no schema is supplied, records the offset after the header row, and marks the virtual table `SQLITE_VTAB_DIRECTONLY`. `csvtabOpen()` opens a fresh reader for each cursor. `csvtabFilter()` rewinds to `iStart`, preallocates the field buffer, and calls `csvtabNext()`. `csvtabNext()` reads fields until a row terminator, copies up to `nCol` fields into cursor column buffers, pads missing trailing columns with NULL, increments rowid, and sets rowid to -1 at EOF. `csvtabBestIndex()` normally reports a full-scan cost; the `SQLITE_TEST` flag can pretend constraints are useful for planner tests.

## State and persistence

The virtual table stores only configuration strings and header offset. It never writes CSV data. Cursor state owns open file handles and field buffers, which are closed/freed on cursor close. Inline `data=` input is scanned from memory.

## Dependencies and integration points

It depends on SQLite virtual table APIs, standard C file IO, and SQLite memory routines. Because `filename=` reads arbitrary files, the module is direct-only and the comments recommend TEMP virtual tables.

## Risks

CSV parsing is RFC4180-oriented but only comma-separated; there is no runtime separator parameter despite a parser comment mentioning alternative separators. Huge fields grow memory dynamically. Header and schema inference reads only the first row, so malformed later rows surface during scan. Filesystem access is intentionally powerful and must remain direct-only. `csv_trim_whitespace()` uses string length bookkeeping that is sensitive to trailing whitespace cases. `csvtabBestIndex()` test mode intentionally lies to the planner and must not be enabled in production builds.

## Test signals

Tests should cover quoted fields, doubled quotes, CRLF and LF endings, empty fields, empty first field, UTF-8 BOM stripping, header inference, explicit schema, `columns=N` padding/truncation, data-vs-filename validation, unreadable files, rowid progression, EOF, direct-only restrictions, and `csv_wr` read-only errors under `SQLITE_TEST`.
