# sources/storage-engines/lmdb/libraries/liblmdb/mtest3.c

## Purpose
`mtest3.c` tests sorted duplicate databases using `MDB_DUPSORT`, including duplicate-data insertion, deletion by key/data pair, and cursor traversal.

## Important APIs, types, and functions
It opens subDB `"id2"` with `MDB_CREATE|MDB_DUPSORT`, uses `mdb_put` with `MDB_NODUPDATA`, deletes with `mdb_del(txn, dbi, &key, &data)`, and traverses duplicates with `MDB_NEXT` and `MDB_PREV`.

## Control flow
Random values are generated. Every group of 16 records shares a key derived from the first value in that group, while the data contains each individual value. After insertion and duplicate skip reporting, the test scans all key/data pairs, then deletes selected duplicate values by reconstructing their group key and exact data. It finishes with forward and reverse scans.

## State and persistence behavior
The program mutates `./testdb` subDB `id2` under fixed mapping and nosync mode. Duplicate values are part of the database state and are ordered according to LMDB's duplicate comparator.

## Dependencies and integration points
The test exercises LMDB duplicate-page handling through the public API, especially the distinction between key uniqueness and key/data uniqueness.

## Risks and edge cases
The random delete step can be zero. `kval` has `sizeof(int)` bytes, and formatted keys like `"abc"` include a NUL only if room permits; key-size assumptions are platform-sensitive. Existing data from previous runs can affect duplicate counts.

## Test signals
Signals include `MDB_KEYEXIST` only for true duplicate data, successful deletion of selected key/data pairs, and ordered cursor output in both directions.
