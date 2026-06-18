# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_c.awk

## Purpose
`et_c.awk` generates the C source file for an `.et` error table.

## Important APIs, Types, and Functions
It parses `error_table`/`et`, `error_code`/`ec`, `prefix`, and `index` directives; computes table bases using the 64-character alphabet and 8-bit error-code range; emits a `text[]` array, `struct error_table`, static fallback link, `initialize_<table>_error_table()`, and Heimdal-compatible `initialize_<table>_error_table_r()`.

## Control Flow
On the table declaration it initializes base arithmetic with high/low chunks to avoid AWK precision limits. For each error code it emits strings, handles continuation lines, fills indexed gaps with reserved messages, and in `END` emits table metadata and registration functions.

## State, Persistence, Dependencies, Risks, and Test Signals
State is AWK variables tracking table name/base/sign/current item count and continuation buffers. Dependencies are AWK numeric behavior and the same encoding constants as `error_table.h`. Risks include regex fragility, precision workarounds, a typo in negative carry variables (`cur_low`/`cur_high`), and continuation edge cases. Test signals are `make check` diffs for simple, continuation, Heimdal, and IMAP generated outputs.
