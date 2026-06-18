# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_right.c

## Purpose
`com_right.c` adds Heimdal/Kerberos4kth compatibility lookup and registration APIs on top of e2fsprogs com_err data structures.

## Important APIs, Types, and Functions
Public functions are `com_right()`, `com_right_r()`, `initialize_error_table_r()`, and `free_error_table()`. It also defines an internal combined allocation struct containing `et_list` and `error_table`.

## Control Flow
Lookup functions linearly scan an explicit `et_list` for a table whose base range contains the code. `initialize_error_table_r()` appends a dynamically allocated table unless the same message array is already present, and falls back to no registration if allocation fails. `free_error_table()` frees a linked list.

## State, Persistence, Dependencies, Risks, and Test Signals
State is caller-owned `et_list` chains independent of the global `_et_list`. Dependencies are `com_err.h` and `error_table.h`. Risks include no locking for caller lists, `com_right_r()` requiring nonzero buffer length, and compatibility allocation layout assumptions. Test signals come from generated Heimdal-style test case initializers and direct lookups against list-local tables.
