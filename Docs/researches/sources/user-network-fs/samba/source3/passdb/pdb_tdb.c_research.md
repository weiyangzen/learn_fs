# sources/user-network-fs/samba/source3/passdb/pdb_tdb.c

## Purpose
`pdb_tdb.c` implements the `tdbsam` passdb backend, Samba's local TDB-backed account database. It persists serialized `struct samu` records by username, maintains a RID-to-username index, stores a monotonic next-RID counter, handles database format upgrades, and exposes passdb operations for local account lookup, mutation, rename, enumeration, and RID allocation.

## Important APIs, Types, And Functions
Persistent keys are defined by prefixes and info keys: `USER_` for lower-cased username records, `RID_` for RID indexes, `NEXT_RID` for allocation, and `INFO/version` plus `INFO/minor_version` for database versioning. Global runtime state includes `db_sam`, `tdbsam_filename`, and booleans `map_builtin`/`map_wellknown`.

Upgrade helpers are `tdbsam_convert_one()`, `backup_copy_fn()`, `tdbsam_convert_backup()`, `tdbsam_upgrade_next_rid()`, `tdbsam_convert()`, and `tdbsam_open()`. Lookup helpers are `tdbsam_getsampwnam()`, `tdbsam_getsampwrid()`, and `tdbsam_getsampwsid()`. Mutation helpers are `tdb_delete_samacct_only()`, `tdbsam_delete_sam_account()`, `tdb_update_samacct_only()`, `tdb_update_ridrec_only()`, `tdb_update_sam()`, `tdbsam_update_sam_account()`, `tdbsam_add_sam_account()`, and `tdbsam_rename_sam_account()`.

RID allocation and enumeration are implemented by `tdbsam_new_rid()`, `tdbsam_collect_rids()`, `tdbsam_search_users()`, and `tdbsam_search_next_entry()`. `pdb_init_tdbsam()` installs the passdb method table, reads configuration booleans for builtin/wellknown mapping responsibility, computes the database path, and stores it globally. `pdb_tdbsam_init()` registers the backend name `tdbsam`.

## Control Flow
All operations call `tdbsam_open()` as needed. Open creates the database with `0600` permissions, reads version keys, rejects newer major versions, and upgrades older versions under a named mutex. Local databases are first copied through `tdbsam_convert_backup()` to a temporary TDB and atomically renamed back, which preserves records across older hash-function behavior. `tdbsam_convert()` starts a transaction, upgrades `NEXT_RID` from old winbind idmap state if missing, traverses all `USER_` records, decodes old buffer formats into `struct samu`, repacks them in the latest format, and stores current version keys before commit.

Name lookup lowercases the requested username, fetches `USER_<name>`, rejects missing or zero-sized records, and unpacks with `init_samu_from_buffer(SAMU_BUFFER_LATEST)`. RID lookup fetches `RID_<hexrid>` to get the username and delegates to name lookup. SID lookup first checks the SID belongs to the local SAM domain and extracts the RID.

Add and update flow runs through `tdb_update_sam()`. It requires a valid user RID, starts a TDB transaction, and for updates fetches the old account to detect RID changes. It stores the serialized `struct samu` under the username key, updates or inserts the RID index, deletes the old RID key if the RID changed, and commits atomically. Delete removes both username and RID keys in one transaction.

Rename requires a configured external `rename user script`. It copies the old account, sets the new username, starts a transaction, inserts the new username record, lowercases old and new names for script substitution, runs the script, flushes the nscd user cache, rewrites the RID index to point to the new name, deletes the old username record, and commits. If the transaction commit fails after the external script succeeded, the code logs that POSIX and passdb state may be inconsistent.

RID allocation uses `dbwrap_trans_change_uint32_atomic_bystring()` on `NEXT_RID`, returning the previous/current value after increment semantics defined by dbwrap. Enumeration traverses `RID_` keys, stores parsed hex RIDs in a dynamic array, and lazily resolves each RID to a `samu` in `tdbsam_search_next_entry()`, skipping users deleted after collection and filtering account-control bits.

## State And Persistence
Persistent state is `passdb.tdb` under `lp_private_dir()` unless a backend location is supplied. It contains serialized `struct samu` values, RID indexes, version metadata, and the next RID counter. Upgrades may create and rename a temporary `*.tmp` database. `tdbsam_upgrade_next_rid()` can read legacy `winbindd_idmap.tdb` `RID_COUNTER` to seed the counter, falling back to `BASE_RID`.

Runtime state is global rather than per-method: `db_sam` is the open db context and `tdbsam_filename` is a process-global path. Reinitializing the backend frees and replaces the filename. The `map_builtin` and `map_wellknown` flags are also global and are returned through passdb responsibility hooks.

## Dependencies And Integration Points
The backend depends on dbwrap/TDB, TDB utility helpers, passdb serialization (`init_samu_from_buffer()`, `init_buffer_from_samu()`), SID helpers, account control APIs, loadparm (`lp_private_dir()`, `lp_rename_user_script()`, `lp_parm_bool()`), named mutexes, `state_path()`, `smbrun()`, nscd cache flushing, and Samba string/hex parsing helpers.

It integrates through the passdb registry as `tdbsam` and provides `PDB_CAP_STORE_RIDS`. Builtin and wellknown SID responsibility is configurable with `tdbsam:map builtin` and `tdbsam:map wellknown`.

## Risks
The backend relies on global process state, so multiple initializations with different locations can replace `tdbsam_filename` for all method instances. Upgrade paths are complex and high-risk: they rewrite every user record, may rename a temporary database over the original, and use `smb_panic()` on some transaction failures. Backup conversion assumes local database semantics and mutex protection.

Transaction boundaries protect TDB keys but not external rename scripts. Rename can leave the Unix account renamed while TDB commit fails, a risk acknowledged in the code. Usernames are lowercased for storage and indexes, so case-preservation semantics depend on the serialized `samu` content rather than key names. RID index corruption can break lookup and enumeration even when user records exist.

Search enumeration snapshots RIDs first, then resolves records later; concurrent deletion is handled, but concurrent modifications can produce changing display data. RID allocation correctness depends on dbwrap atomic counter behavior and on no external writers corrupting `NEXT_RID`.

## Test Signals
Tests should cover opening a fresh database, version-key initialization, upgrades from SAMU buffer versions 0 through 4, conversion rollback on malformed records, temporary backup rename behavior, missing and migrated `NEXT_RID`, newer-version rejection, name/RID/SID lookup, zero-sized record rejection, add/update/delete transaction behavior, RID change updates, RID index corruption, new RID allocation monotonicity, search filtering and concurrent deletion tolerance, builtin/wellknown responsibility configuration, and rename-script success/failure including commit-failure injection.
