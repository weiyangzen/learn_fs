# sources/storage-engines/lmdb/libraries/liblmdb/mtest6.c

## Purpose
`mtest6.c` is a focused split/merge test for integer-key databases with large values that force B-tree page splits.

## Important APIs, types, and functions
It opens subDB `"id6"` with `MDB_INTEGERKEY`, uses a cursor for `mdb_cursor_put`, formats integer keys with `mdb_dkey` for display, and sizes values from the database page size returned by `mdb_stat`.

## Control flow
The test opens `./testdb`, creates the integer-key DB, allocates a value buffer roughly one quarter of a page, then inserts three waves of 12 records each with interleaved key sequences (`i*5`, `i*5+4`, `i*5+1`). These insertion orders are intended to trigger multiple splits. It scans from first to last and closes. A deletion/merge section remains disabled under `#if 0`.

## State and persistence behavior
It persists subDB `id6` under fixed-map/nosync mode. Large values and integer keys shape page layout and split behavior; the disabled block would have tested merges but is not active.

## Dependencies and integration points
This file depends on LMDB integer-key comparator semantics and internal page-size behavior. It also uses `mdb_dkey`, an LMDB debugging formatter.

## Risks and edge cases
The code does not check `mdb_txn_commit` through `E` at the final commit. `sval` is heap allocated but not freed. The disabled block references variables that are unused in active code, suggesting this is a narrow reproducer rather than a polished test.

## Test signals
Expected signals are successful insertion of all waves, ordered integer-key traversal, and no split-related assertion or corruption. Enabling the disabled block would add merge coverage.
