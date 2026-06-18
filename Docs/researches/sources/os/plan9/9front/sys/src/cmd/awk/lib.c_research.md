# File Research: sources/os/plan9/9front/sys/src/cmd/awk/lib.c

Implements awk record/field handling, command-line variable handling, diagnostics, and numeric conversion helpers.

Key responsibilities:
- Initializes `$0`, field cells, record buffers, and field tables.
- Opens input files or stdin based on `ARGV`, processing command-line `var=value` assignments in order.
- Reads records according to `RS`, including blank-line paragraph behavior for empty `RS`.
- Splits records into fields based on default whitespace, single-character FS, empty FS as UTF character fields, or regex FS.
- Rebuilds `$0` from fields using `OFS` when fields are modified.
- Grows field tables dynamically.
- Implements error reporting with source/input context and brace/bracket/paren checks.
- Provides fatal/warning handlers and numeric parsing via integer/float logic.

Important interfaces:
- Exports `recinit`, `getrec`, `readrec`, `nextfile`, `fldbld`, `fieldadr`, `recbld`, `SYNTAX`, `FATAL`, `WARNING`, `to_number`, and related helpers.
- Uses regex APIs `compre`, `nematch`, `releasere`.
- Uses symbol APIs `lookup`, `setsval`, `setfval`, `setsymtab`, `getsval`.

Notes:
- `inputFS` snapshots FS at input time so later field splitting uses the correct separator.
- Error context printing relies on lexer buffer globals `ebuf` and `ep`.
