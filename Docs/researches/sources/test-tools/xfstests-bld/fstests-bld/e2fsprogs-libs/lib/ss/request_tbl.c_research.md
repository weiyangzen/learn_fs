# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/request_tbl.c

## Purpose
`request_tbl.c` manages the ordered list of request tables attached to an ss invocation.

## Important APIs, Types, and Functions
Public functions are `ss_add_request_table()` and `ss_delete_request_table()`.

## Control Flow
Add counts existing tables, reallocates space for a new entry plus NULL terminator, clamps insertion position, shifts entries down, inserts the new table, and returns status via `code_ptr`. Delete compacts all entries not equal to the requested pointer and reports whether anything was removed.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.rqt_tables`. Dependencies are request-table layout and generated ss error codes. Risks include a likely allocation-size bug using `sizeof(ssrt)` instead of pointer size, delete setting success when nonmatching entries exist rather than when a match is removed, and no duplicate handling. Test signals include adding standard requests after test commands and deleting tables in lifecycle tests.
