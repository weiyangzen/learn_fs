# sources/storage-engines/lmdb/libraries/liblmdb/mtest_remap.c

## Purpose
`mtest_remap.c` repeats the basic main-database tester while opening the environment with `MDB_REMAP_CHUNKS`, exercising LMDB's chunk remapping mode.

## Important APIs, types, and functions
It uses the standard test macros, opens `./testdb` with `MDB_REMAP_CHUNKS`, then uses core APIs including `mdb_put`, `mdb_del`, `mdb_cursor_get`, cursor deletion, and transaction commit/abort.

## Control flow
The workflow matches `mtest.c`: generate random records, configure max readers and map size, open the remapped environment, insert records, scan, delete random records, scan forward/backward, delete initial records through a cursor, restart cursor traversal inside the write transaction, commit, and verify traversal in a new transaction.

## State and persistence behavior
The test persists data in `./testdb` using remapped chunks rather than a single traditional mapping mode. This changes how pages are mapped in memory while preserving LMDB's logical database semantics.

## Dependencies and integration points
It includes `chacha8.h` but does not use encryption; the meaningful integration point is the `MDB_REMAP_CHUNKS` environment flag in liblmdb.

## Risks and edge cases
The same random zero-stride delete risk from `mtest.c` applies. Including an unused crypto header can create unnecessary build dependency. Remap behavior is platform-sensitive and may expose mapping or pointer-lifetime assumptions in cursor code.

## Test signals
Successful completion under remap mode, stable cursor traversal across deletes and transaction boundaries, and comparison with the baseline `mtest.c` behavior are the key signals.
