# sources/storage-engines/lmdb/libraries/liblmdb/mtest2.c

## Purpose
`mtest2.c` repeats the basic `mtest.c` workflow against a named subdatabase, validating subDB creation and access.

## Important APIs, types, and functions
The macro pattern matches other LMDB tests. `main` uses `mdb_env_set_maxdbs`, opens environment `./testdb`, creates DBI `"id1"` with `MDB_CREATE`, inserts with `MDB_NOOVERWRITE`, reads with a cursor, deletes records with `mdb_del`, and scans forward/backward.

## Control flow
The test generates random values, creates a maxdbs-capable environment, opens subDB `id1` in a write transaction, inserts records, commits, scans in a read-only transaction, deletes random records in separate write transactions, frees input data, and performs final forward and reverse cursor scans before closing.

## State and persistence behavior
It persists data in the `id1` subdatabase inside `./testdb`. The environment uses `MDB_FIXEDMAP|MDB_NOSYNC`, so durability is weaker and address mapping is stricter than default.

## Dependencies and integration points
This executable links directly to LMDB and verifies that named DBs work when `mdb_env_set_maxdbs` is configured before open.

## Risks and edge cases
Like `mtest.c`, delete loop step `rand()%5` can be zero. It also uses `sizeof(int)` key size against a formatted string buffer. `MDB_NOSYNC` can leave a corrupt environment after system crash during testing, and repeated runs reuse an existing `./testdb`.

## Test signals
Successful subdatabase creation, duplicate reporting, cursor traversal, and clean close are the primary signals. Repeating under stress helps expose nondeterministic loop and existing-data interactions.
