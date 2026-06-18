## sources/user-network-fs/samba/source4/kdc/sdb.h

Purpose: definition of Samba's KDC database-neutral SDB representation and fetch flags.

Important types: `sdb_salt`, `sdb_key`, `sdb_keys`, `sdb_event`, `sdb_etypes`, `SDBFlags`, `sdb_pub_key`, `sdb_pub_keys`, certificate mapping structures, and `sdb_entry`. `sdb_entry` includes principal, kvno, current/old keys, etypes/session etypes, creation/modification events, validity/password lifetimes, KDC flags, PKINIT key trust data, certificate mappings, object SID, and attached `samba_kdc_entry`.

Important constants: SDB error codes (`SDB_ERR_NOENTRY`, `SDB_ERR_NOT_FOUND_HERE`, `SDB_ERR_WRONG_REALM`) and fetch flags for decrypt, replace, client/server/krbtgt, canonicalization, admin data, kvno, AS/TGS, armor/user2user/cross-realm/S4U, force-canon, and RODC number.

Control flow and integration: SDB is the common shape fetched from Samba DSDB before conversion into Heimdal HDB or MIT KDB entries. `SDB_F_HDB_MASK` documents the subset compatible with Heimdal HDB.

State and persistence: declarations only; SDB values are transient snapshots of DSDB state plus derived metadata.

Dependencies: Kerberos types and generated security SID types.

Risks: `SDBFlags` is asserted to match Heimdal `HDBFlags` size in conversion; layout drift is dangerous. Fetch flag combinations control KDC authorization semantics and must be mapped carefully from MIT/Heimdal callers.

Test signals: compile-time flag/layout checks, fetch flag mapping from AS/TGS/S4U paths, and conversion tests for all optional entry fields.
