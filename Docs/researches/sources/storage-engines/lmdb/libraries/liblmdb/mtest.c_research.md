# sources/storage-engines/lmdb/libraries/liblmdb/mtest.c

## Purpose
`mtest.c` is a toy regression program that exercises basic LMDB main-database writes, duplicate-skip behavior, deletes, cursor scans, and cursor restarts.

## Important APIs, types, and functions
The program uses `E`, `RES`, and `CHECK` macros to enforce LMDB return codes. `main` calls environment setup APIs, transaction begin/commit/abort, `mdb_dbi_open`, `mdb_put`, `mdb_del`, `mdb_env_stat`, `mdb_cursor_open`, and cursor traversal operations including `MDB_NEXT`, `MDB_LAST`, `MDB_PREV`, and `MDB_FIRST`.

## Control flow
It generates a random number of integer-derived string records, opens `./testdb` with fixed mapping, inserts records with `MDB_NOOVERWRITE`, prints all records in a read transaction, deletes a random stride of records in individual transactions, then scans forward/backward. It also deletes the first 50 records using a cursor, tests cursor reuse within the same write transaction, and opens a fresh transaction to confirm post-commit traversal.

## State and persistence behavior
The test mutates `./testdb` in the current directory. It uses a 10 MiB map, 1024-byte pages, one max reader, and default synchronous behavior unless code comments are toggled. Random data makes each run nondeterministic.

## Dependencies and integration points
It is a simple executable linked against liblmdb and serves as a smoke test for core B-tree operations.

## Risks and edge cases
The key is declared as `sizeof(int)` bytes but points to a formatted string buffer, so only the first integer-sized bytes of the string key participate. Random stride `rand()%5` can be zero, causing an infinite loop. Fixed-map opening can fail on platforms where the chosen address is unavailable.

## Test signals
The expected signal is successful completion with printed insert/delete/scan output. Sanitizer or repeated stress runs can reveal the zero-stride bug and cursor invalidation issues.
