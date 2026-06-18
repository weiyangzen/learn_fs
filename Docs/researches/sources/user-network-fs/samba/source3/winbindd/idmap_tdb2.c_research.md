# sources/user-network-fs/samba/source3/winbindd/idmap_tdb2.c

## Purpose
This backend is a TDB-backed idmap variant intended for clustered Samba setups. It stores mappings in `idmap2.tdb` under the private directory and can optionally consult an external script to populate missing mappings.

## Important APIs, Types, And Functions
`struct idmap_tdb2_context` stores the optional script path. Helpers include `idmap_tdb2_init_hwm`, `idmap_tdb2_open_db`, `idmap_tdb2_set_mapping`, `idmap_tdb2_script`, `idmap_tdb2_id_to_sid`, `idmap_tdb2_sid_to_id`, and `idmap_tdb2_db_init`. It uses `idmap_tdb_common_context` for common batch lookup/allocation.

## Control Flow
Initialization creates common and backend-specific contexts, reads `script` config with deprecated fallback for `idmap:script`, copies the script path for reload safety, installs custom single-lookup hooks and RW ops, opens `lp_private_dir()/idmap2.tdb`, and initializes HWM records. Lookups first try dbwrap records. Missing records call the script when configured, parse `UID:`, `GID:`, or `SID:` output, range-filter returned IDs, and store bidirectional records in a transaction. Allocation uses common HWM logic and can create mappings through `idmap_rw_new_mapping`.

## State And Persistence
State is persisted in `idmap2.tdb` with `USER HWM`, `GROUP HWM`, and bidirectional string records. Optional script-derived results are cached into the TDB. Unlike `idmap_tdb.c`, this file does not contain old-format upgrade logic.

## Dependencies And Integration
It depends on dbwrap, TDB helpers, idmap common code, config APIs, optional shell script execution with `popen`, and Samba SID parsing. It registers under `tdb2`.

## Risks And Test Signals
Test DB path configuration, HWM creation, script fallback, malformed script output, script IDs outside range, collision handling, missing script behavior, and concurrent store attempts. The script command is assembled as a shell string and executed with `popen`, so quoting/injection behavior and whitespace in script paths or arguments deserve specific tests.
