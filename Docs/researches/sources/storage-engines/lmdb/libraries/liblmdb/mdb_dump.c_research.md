# sources/storage-engines/lmdb/libraries/liblmdb/mdb_dump.c

## Purpose
`mdb_dump.c` serializes LMDB databases in a Berkeley DB-compatible dump format, or emits LMDB incremental dumps from a transaction ID.

## Important APIs, types, and functions
`flagbit` maps LMDB DB flags to dump header keywords. `hex`, `text`, and `dobyte` encode keys and values in printable or hex form. `dumpit` emits headers, opens a cursor, iterates records with `MDB_NEXT`, and writes `DATA=END`. `main` handles `-a`, `-s`, `-l`, `-f`, `-i`, `-n`, `-L`, `-p`, `-v`, `-V`, `-m`, and `-w`.

## Control flow
The command parses options, installs signal handlers, creates and optionally crypto-configures an environment, opens it read-only, and branches to incremental dump APIs when `-i` is supplied. Normal dumps optionally redirect stdout, begin a read-only transaction, open a DBI, then either dump one database or scan the main database for subdatabase records with `mdb_cursor_is_db`. `-l` lists subdatabase names instead of dumping their contents.

## State and persistence behavior
All normal database access is read-only and snapshot based. `MDB_PREVSNAPSHOT` requests an older snapshot; `MDB_NOLOCK` bypasses reader locking. Output includes map size, map address, max readers, page size, DB flags, and each key/value pair, so it captures logical database contents and load-critical metadata.

## Dependencies and integration points
The dump format is consumed by `mdb_load.c`. Incremental mode integrates with `mdb_env_incr_dump` and `mdb_env_incr_dumpfd`. Crypto handling uses `module.c` helpers.

## Risks and edge cases
Printable mode only escapes backslash and non-printable bytes, so consumers must use the matching parser. Listing all DBs relies on main-DB entries being named subdatabases. Incremental dumps bypass the text header format. Signal interruption returns `EINTR`, but partial output may already be written. `-L` can expose inconsistent snapshots when used carelessly.

## Test signals
Round-trip tests with `mdb_load`, printable and bytevalue formats, all supported DB flags, all-subDB/list modes, output-file errors, incremental dump/load, encrypted DBs, and interrupted stdout writes are important.
