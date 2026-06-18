# sources/user-network-fs/samba/source3/utils/net_idmap.c

## Purpose
This file implements the local `net idmap` command family for inspecting and mutating Samba ID mapping databases. It supports classic `tdb`/`tdb2` idmap databases and selected `autorid` database operations, plus LDAP/rfc2307 idmap secret storage.

## Important APIs, Types, And Control Flow
The command entrypoint is `net_idmap()`, which dispatches `dump`, `restore`, `get`, `set`, `delete`, and `check` through `net_run_function`. `enum idmap_dump_backend` and `struct net_idmap_ctx` track whether the active database is classic TDB or autorid. `net_idmap_dbfile()` chooses a database path from `--db`, `lp_idmap_default_backend()`, `state_path()`, or `lp_private_dir()`. Dump traversal uses `net_idmap_dump_one_tdb_entry()` or `net_idmap_dump_one_autorid_entry()`. Restore parses lines such as `UID n SID`, `GID n SID`, `USER HWM`, and `GROUP HWM` and writes reciprocal mappings with `net_idmap_store_id_mapping()`. Delete paths include bidirectional mapping deletion with optional force and autorid range deletion by range number, SID/index, or all domain ranges. Autorid get/set commands use the `idmap_autorid_*` helper API. `net_idmap_check()` translates global CLI flags into `struct check_options` and calls `net_idmap_check_db()`.

## State And Persistence
The file reads and writes persistent TDB databases: `winbindd_idmap.tdb`, `idmap2.tdb`, or `autorid.tdb`, unless `--db` overrides the path. Restore and delete operations use transactions or `dbwrap_trans_do()` for atomicity. Autorid write operations initialize/open the autorid database through `idmap_autorid_db_init()`. `net_idmap_secret()` writes credentials into Samba secrets storage under an uppercased `IDMAP_<backend>_<domain>` key.

## Dependencies And Integration Points
It depends on Samba configuration, dbwrap/TDB, secrets storage, idmap core types, `idmap_autorid_tdb.h`, SID/security helpers, `net_idmap_check.h`, and `smb_strtox`. It integrates into the broader `net` CLI through `net_proto.h` and shares global option fields on `struct net_context`.

## Risks And Test Signals
Risk centers on destructive local database edits, backend gating, and textual restore parsing. `parse_uint32()` accepts values with possible crop to `uint32_t`. Restore line buffers are fixed size and invalid lines are ignored rather than fatal. Non-TDB backends are mostly rejected, but `--db` still leaves backend context defaulting to TDB. Test with TDB dumps/restores, malformed restore lines, reciprocal mapping deletion with and without `-f`, autorid range get/set/delete/config operations, unsupported backends, and dry/auto idmap check modes.
