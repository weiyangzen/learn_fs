# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/init_et.c

## Purpose
`init_et.c` implements an older com_err table-registration API that dynamically creates an error table from raw messages, base, and count.

## Important APIs, Types, and Functions
The public function is `init_error_table()`. It uses an internal `struct foobar` containing both `et_list` and `error_table`, and appends to external `_et_dynamic_list`.

## Control Flow
The function treats zero base/count or NULL messages as no-op success, allocates the combined node, fills table pointers/base/count, links it at the head of `_et_dynamic_list`, and returns `ENOMEM` on allocation failure.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the global dynamic table list. Dependencies are `com_err.h` and `error_table.h`. Risks include no list locking, no duplicate detection, and allocations that are not removed unless callers use compatible removal APIs. Test signals are legacy users successfully resolving codes registered with `init_error_table()`.
