<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c

## Purpose

`nfsdcld/sqlite.c` implements the SQLite persistence backend for the daemon's NFSv4 client recovery database. It manages schema creation/upgrades, epoch transitions, client insert/remove/check operations, recovery iteration, and migration from `nfsdcltrack` and legacy recovery directories.

## Important APIs, types, and functions

Public APIs include `sqlite_prepare_dbh`, `sqlite_insert_client`, `sqlite_insert_client_and_princhash`, `sqlite_remove_client`, `sqlite_check_client`, `sqlite_grace_start`, `sqlite_grace_done`, `sqlite_iterate_recovery`, `sqlite_delete_cltrack_records`, `sqlite_first_time_done`, and `sqlite_shutdown`. Schema helpers handle versions 1-4, table-name repair, attached cltrack database copying, and first-time flags.

## Control flow

Preparation opens `<storagedir>/main.sqlite`, creates the directory if needed, sets a busy timeout, detects schema version, initializes or upgrades to v4, loads current/recovery epochs, checks table names under an exclusive transaction, and performs first-time migration. Grace start either advances `current`/`recovery` and creates a new `rec-...` table, or clears the current table when restarting while already in grace. Grace done clears recovery, drops the recovery table, and updates globals. Check queries the recovery table and reinserts reclaimed clients into the current epoch.

## State and persistence behavior

The database has `parameters`, `grace`, and per-epoch `rec-%016"PRIx64"` tables with `id` and optional `princhash` blobs. `current_epoch`, `recovery_epoch`, and `first_time` globals mirror database values. Migration can attach the old cltrack database, copy its `clients` table, load legacy recdir entries, and later delete migrated old records.

## Dependencies and integration points

It depends on sqlite3, config parsing for old cltrack storage location, `cld-internal.h` globals/message buffers, legacy migration, NFS4 opaque limits, and `xlog`. `nfsdcld.c` calls it for every kernel upcall.

## Risks and edge cases

Dynamic SQL uses formatted table names and fixed `PATH_MAX` buffers; bounds checks are present but numerous. `sqlite_iterate_recovery` copies principal hash bytes using `SHA256_DIGEST_SIZE` when any bytes exist, without first ensuring the SQLite blob length is at least that size. Some functions return sqlite codes while callers map them to generic kernel errors. Schema repair only accepts short table names for current or recovery epochs.

## Test signals

Tests should cover new DB init, upgrades from v1/v2/v3, concurrent setup races, first-time cltrack and legacy migration, epoch advance and restart-in-grace, check success/failure, principal hash storage/iteration, table-name repair, busy database handling, attach/detach failures, grace done table drops, and shutdown idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c -->
