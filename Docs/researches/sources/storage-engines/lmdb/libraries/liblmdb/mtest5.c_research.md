# sources/storage-engines/lmdb/libraries/liblmdb/mtest5.c

## Purpose
`mtest5.c` mirrors `mtest3.c` but performs duplicate inserts through `mdb_cursor_put`, validating cursor-based duplicate writes.

## Important APIs, types, and functions
It uses the standard LMDB test macros, opens subDB `"id2"` with `MDB_DUPSORT`, opens a write cursor, inserts via `mdb_cursor_put(..., MDB_NODUPDATA)`, then uses `mdb_del` and cursor scans.

## Control flow
The program creates random values, starts a write transaction, opens the duplicate DBI and cursor, groups records by key every 16 values, inserts duplicate data through the cursor, closes the cursor, and commits. It then scans all records, deletes a random subset by exact key/data pair in separate transactions, and verifies remaining data with forward and reverse scans.

## State and persistence behavior
State is written to `./testdb` subDB `id2` using fixed-map/nosync environment flags. Cursor-put semantics must persist the same logical state as direct `mdb_put` in `mtest3.c`.

## Dependencies and integration points
This is an integration test for cursor insertion paths in duplicate-sorted databases, including duplicate rejection behavior.

## Risks and edge cases
The random delete loop can fail to progress when `rand()%5` is zero. It shares the key-size and existing-environment caveats of `mtest3.c`. Cursor closure before commit is required; missing it would stress cleanup behavior differently.

## Test signals
Important signals are duplicate counts matching direct-put behavior, successful cursor-based insertion, and equivalent traversal/deletion results to `mtest3.c`.
