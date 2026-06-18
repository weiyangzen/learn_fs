# sources/storage-engines/lmdb/libraries/liblmdb/mdb_drop.c

## Purpose
`mdb_drop.c` is the LMDB command-line tool for clearing or deleting the main database or a named subdatabase inside an environment.

## Important APIs, types, and functions
`usage` prints the command syntax. `dumpsig` sets the global `gotsig`, although the main flow does not currently branch on it. `main` uses `getopt` to parse `-d`, `-s`, `-n`, `-L`, `-V`, `-m`, and `-w`; then it calls `mdb_env_create`, optional `mdb_modload`/`mdb_modsetup`, `mdb_env_set_maxdbs`, `mdb_env_open`, `mdb_txn_begin`, `mdb_open`, `mdb_drop`, and `mdb_txn_commit`.

## Control flow
After option validation, the tool installs signal handlers, creates the environment, loads optional crypto hooks, sets `maxdbs` to allow subdatabase opens, and opens the target environment. A write transaction opens either the named subdatabase or main database, then `mdb_drop(txn, dbi, delete)` either empties it or removes it depending on `-d`. Cleanup labels abort an uncommitted transaction and close/unload resources.

## State and persistence behavior
This is a destructive writer. Without `-d`, database contents are removed but the DBI remains. With `-d`, the database itself is deleted from the environment. The change persists only after `mdb_txn_commit`; earlier failures abort the transaction.

## Dependencies and integration points
The tool depends on the LMDB write transaction API, subdatabase metadata semantics, POSIX `getopt`, and optional crypto-module hooks.

## Risks and edge cases
The default target is the main DB, so omitting `-s` can erase primary data. `MDB_NOLOCK` is dangerous for a writer if other processes are active. `gotsig` is set but unused, so a signal does not proactively cancel after handlers run. A failed commit jumps through `txn_abort` with `txn` still non-null; LMDB commit failures should leave the transaction invalid, so this path depends on library behavior.

## Test signals
Tests should cover emptying versus deleting subDBs, main DB drops, encrypted databases, NOSUBDIR, failure to open missing subDBs, and recovery after aborted transactions.
