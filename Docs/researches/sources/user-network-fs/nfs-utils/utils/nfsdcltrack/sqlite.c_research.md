<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c

## Purpose

`nfsdcltrack/sqlite.c` provides SQLite storage for the older kernel usermode-helper client tracker.

## Important APIs, types, and functions

Public functions are `sqlite_prepare_dbh`, `sqlite_insert_client`, `sqlite_remove_client`, `sqlite_check_client`, `sqlite_remove_unreclaimed`, and `sqlite_query_reclaiming`. Private helpers create the storage directory, query schema version, initialize schema v2, and upgrade v1 to v2 by adding `has_session`.

## Control flow

Preparation opens `<storagedir>/main.sqlite`, creates the directory if open fails, sets busy timeout, then initializes or upgrades the schema. Inserts use `INSERT OR REPLACE` into `clients`, setting `time` to either zero or current epoch seconds and storing the session flag. Checks verify record existence and update timestamp only for NFSv4.0 clients. Grace completion deletes records with timestamps older than the supplied grace start. Reclaim query counts records that are older than grace start or lack sessions.

## State and persistence behavior

The database has `parameters` and `clients` tables. Client rows contain binary `id`, integer `time`, and integer `has_session`. The sqlite handle and SQL scratch buffer are process-global for the helper invocation.

## Dependencies and integration points

It depends on sqlite3, Linux `PATH_MAX`, xlog, and the command helper in `nfsdcltrack.c`. `nfsdcld/sqlite.c` can later attach this database and migrate its `clients` records.

## Risks and edge cases

Errors can be raw sqlite codes or negative errno values. `sqlite_query_reclaiming` returns sqlite error codes as nonzero counts to callers, which conservatively prevents grace lifting. No explicit shutdown closes `dbh` in this file, relying on process exit. Time is sourced from SQLite `strftime`.

## Test signals

Tests should cover new DB creation, v1 upgrade, unsupported schema rejection, inserts with current/zero time, session vs non-session check timestamp behavior, removal, pruning by grace time, reclaim counts, busy timeout behavior, and storage path errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c -->
