# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/invocation.c

## Purpose
`invocation.c` creates and destroys ss subsystem invocation records.

## Important APIs, Types, and Functions
Public functions are `ss_create_invocation()` and `ss_delete_invocation()`.

## Control Flow
Creation allocates or grows `_ss_table`, initializes the generated ss error table, finds an unused index, fills `ss_data` fields including prompt, request-table list, info dirs, flags, and optional readline support. Deletion frees prompt, request tables, info directories, optional readline resources, and the `ss_data` object.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_table` and per-invocation `ss_data`. Dependencies include generated `initialize_ss_error_table()`, optional `ss_get_readline()`, and request tables. Risks include unchecked allocations, not clearing `_ss_table[sci_idx]` on delete, one-based sparse indexing, and no thread safety. Test signals are `test_ss` startup/shutdown, standard request-table addition, and repeated invocation lifecycle tests.
