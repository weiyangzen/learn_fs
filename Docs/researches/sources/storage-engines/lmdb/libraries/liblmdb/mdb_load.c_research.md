# sources/storage-engines/lmdb/libraries/liblmdb/mdb_load.c

## Purpose
`mdb_load.c` loads databases from `mdb_dump` text output, plaintext key/value input, or LMDB incremental dump streams.

## Important APIs, types, and functions
`readhdr` parses dump headers into global environment info, page size, subdatabase name, and DB flags. `readline` decodes one key or value in print, bytevalue, no-header, or plaintext mode. `unhex` decodes hex pairs. `greater` is a comparator used to enable append loading without full ordering checks. `main` configures the environment and batches cursor puts.

## Control flow
The command parses input-mode and environment options, optionally reopens stdin, reads the first dump header unless `NOHDR` is set, creates and optionally crypto-configures the environment, and branches to `mdb_env_incr_loadfd` for incremental mode. Normal mode applies header-derived max readers, mapsize, page size, and fixed-map address before opening the environment. It then loops over dump sections: begin write transaction, open/create the DBI, optionally set append comparators, open a cursor, read key/value pairs, put records, commit every 100 records, sync if `MDB_NOSYNC`, close DBI, and continue until EOF.

## State and persistence behavior
The loader mutates the target environment. Header metadata can change environment map size, max readers, page size, and fixed mapping. `-N` avoids overwriting existing records. `-Q`/default `MDB_NOSYNC` accelerates loading but relies on a final forced sync for durability. Incremental mode delegates persistence to LMDB's incremental loader.

## Dependencies and integration points
It is tightly coupled to `mdb_dump.c`'s header and data encoding. It uses LMDB environment setters, DB flag constants, cursor puts, duplicate handling, and optional crypto-module setup.

## Risks and edge cases
Most parsing state is global, so malformed multi-database input can leak prior header values. `readline` resizes buffers but uses C string length, so embedded NUL input in text mode is treated as invalid. Append mode changes comparators to a comparator that always returns greater, relying on the caller's sorted input. A commit every 100 records opens a new transaction but keeps using the earlier DBI handle, which is valid only under LMDB's DBI lifetime rules. Bad dumps can partially load earlier committed batches.

## Test signals
Round trips from bytevalue and printable dumps, multi-subDB dumps, duplicate/fixed/integer flags, no-overwrite behavior, plaintext `-T`, append `-a`, incremental streams, crash between batches, encrypted inputs, and malformed escape/header lines should be covered.
