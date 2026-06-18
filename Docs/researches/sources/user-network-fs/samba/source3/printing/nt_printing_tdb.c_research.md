# sources/user-network-fs/samba/source3/printing/nt_printing_tdb.c

Purpose: upgrades old NT printing TDB databases through schema versions before full migration to the registry-backed model. It moves records into separate databases, fixes security descriptors, normalizes printer keys, and records the current database version.

Important APIs and functions: `nt_printing_tdb_upgrade()` is the exported entry point. It opens `ntdrivers.tdb`, `ntprinters.tdb`, and `ntforms.tdb`, reads `INFO/version`, and upgrades to version 5. `upgrade_to_version_3()` moves `FORMS/` records to `ntforms.tdb` and `PRINTERS/` plus `SECDESC/` records to `ntprinters.tdb`. `upgrade_to_version_4()` traverses printer security descriptors with `sec_desc_upg_fn()`, remapping generic access masks to printer-specific rights and adding Builtin Administrators owner/group. `upgrade_to_version_5()` lowercases printer and secdesc keys through `normalize_printers_fn()`.

Control flow: missing all three databases is success. Fresh driver database receives version 5. Version 1 or endian-reversed version 1 moves records to split databases and stores version 3. Version 2 or endian-reversed version 2 is normalized to version 3. Version 3 applies security descriptor fixes, version 4 normalizes keys, and unknown versions fail.

State and persistence: mutates TDB files in place using `tdb_store`, `tdb_delete`, and `tdb_store_int32`. Static TDB handles are closed and nulled on all exit paths.

Dependencies and integration: uses `state_path()`, TDB utilities, generated spoolss/security constants, security descriptor marshalling helpers, and global Builtin Administrators SID. It runs before the later TDB-to-winreg migration path.

Risks: upgrades are not transactional across the three TDBs, so interruption can leave mixed versions. `upgrade_to_version_3()` stores moved records before deleting originals. Bad secdesc records are deleted. `normalize_printers_fn()` deletes before storing under the new key, risking data loss on store failure. Tests should use fixture TDBs for versions 1-5, endian-reversed versions, malformed security descriptors, mixed-case keys, and interruption/retry idempotence.
