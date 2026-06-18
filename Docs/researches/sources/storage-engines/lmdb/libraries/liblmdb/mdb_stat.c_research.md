# sources/storage-engines/lmdb/libraries/liblmdb/mdb_stat.c

## Purpose
`mdb_stat.c` is the LMDB environment inspection tool. It prints environment information, reader table state, freelist details, and B-tree statistics for the main DB or subdatabases.

## Important APIs, types, and functions
`prstat` formats `MDB_stat` fields. `main` parses `-a`, `-s`, `-e`, repeated `-f`, repeated `-r`, `-n`, `-L`, `-v`, `-V`, `-m`, and `-w`, then uses `mdb_env_stat`, `mdb_env_info`, `mdb_reader_list`, `mdb_reader_check`, `mdb_txn_begin`, `mdb_cursor_open`, `mdb_stat`, and `mdb_dbi_open`.

## Control flow
After opening a read-only environment with optional crypto hooks, the tool prints environment info if requested. Reader-table mode lists readers and, with repeated `-r`, clears stale readers before listing again. Freelist mode scans DBI 0 records to count free pages and optionally prints spans and page IDs. It then opens the requested DBI, prints its stats, and with `-a` scans named subdatabase entries and prints each subDB's stats.

## State and persistence behavior
Most behavior is read-only. The exception is `mdb_reader_check`, which can clean stale reader table slots. `MDB_PREVSNAPSHOT` changes the snapshot inspected. Freelist introspection reads LMDB internal DBI 0 state directly.

## Dependencies and integration points
The tool integrates with LMDB public stat APIs and internal freelist layout conventions where freelist data begins with a count followed by page IDs. Optional encryption support mirrors other LMDB utilities.

## Risks and edge cases
Freelist decoding assumes stable internal record layout and can mislead if that representation changes. `MDB_NOLOCK` affects reader table accuracy. `-r` without DB/stat options exits after reader output. `maxdbs` is set to 4 only for subDB/all modes; environments with many named DBs are still scanned by opening one at a time.

## Test signals
Useful tests include environment info, reader list/check behavior with stale readers, freelist verbosity levels, all-subDB scans, previous snapshot reads, encrypted environments, and corrupted freelist sequence detection output.
