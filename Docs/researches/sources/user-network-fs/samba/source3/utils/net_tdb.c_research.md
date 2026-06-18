# sources/user-network-fs/samba/source3/utils/net_tdb.c

## Purpose
Provides `net tdb` diagnostics for selected Samba TDB records and exposes smbXsrv cleanup under `net tdb smbXsrv wipedbs`.

## Important APIs, Types, and Functions
`net_tdb_locking()` initializes locking read-only, converts a hex key into `struct file_id`, fetches share-mode data with `fetch_share_mode_unlocked()`, optionally dumps with `share_mode_data_dump()`, or prints path/name/count with share-mode helpers. `net_tdb_smbXsrv()` dispatches to `net_serverid_wipedbs()`.

## Control Flow
`net_tdb()` dispatches `locking` and `smbXsrv`. `locking` validates the key length, fetches a record, and chooses summary vs `dump`. `smbXsrv` has a nested function table with only `wipedbs`.

## State and Persistence
Locking inspection is read-only. The smbXsrv wipe path can delete stale runtime database records through `net_serverid_wipedbs()`.

## Dependencies and Integration Points
Depends on share-mode locking APIs, open-file NDR headers, common net dispatch, and `net_serverid.c`.

## Risks
Incorrect keys are rejected, but the not-found diagnostic references `argv[1]` where `argv[0]` is likely intended. Cleanup risk is inherited from serverid wipe logic.

## Test Signals
Cover missing/malformed keys, not-found records, summary and dump output, read-only locking init failure, and `net tdb smbXsrv wipedbs` dry-run dispatch.
