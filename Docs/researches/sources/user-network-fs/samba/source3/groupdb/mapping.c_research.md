# sources/user-network-fs/samba/source3/groupdb/mapping.c

## Purpose
`mapping.c` is the passdb-facing group mapping facade. It initializes the selected mapping backend, exposes default passdb group/alias mapping methods, handles Unix group management scripts, creates aliases and builtin aliases, and translates backend alias membership data into SAMR/LSA-style results.

## Important APIs, Types, And Functions
- Static `backend` points at the active `struct mapping_backend`, currently initialized via `groupdb_tdb_init()`.
- `add_initial_entry()` creates a `GROUP_MAP` from gid, SID string, SID type, NT name, and comment.
- `get_domain_group_from_sid()` validates that a SID maps to a domain group and that its gid exists in NSS, with a special fallback for domain RID 513.
- `smb_create_group()`, `smb_delete_group()`, `smb_set_primary_group()`, `smb_add_user_group()`, and `smb_delete_user_group()` execute configured administrative scripts and flush NSS/group caches.
- `pdb_default_getgrsid()`, `pdb_default_getgrgid()`, `pdb_default_getgrnam()`, add/update/delete/enum functions, and alias membership methods adapt backend bool/NTSTATUS APIs to passdb method signatures.
- `pdb_default_create_alias()` and `pdb_create_builtin_alias()` allocate or compose SIDs/gids and store alias mappings.
- `pdb_nop_*` functions provide failure-only implementations for passdb backends without group mapping.

## Control Flow
Most passdb calls first call `init_group_mapping()`, which lazily initializes the backend once. Lookup and mutation wrappers then dispatch directly to backend function pointers. Alias creation checks for existing names with `lookup_name()`, allocates a RID with `pdb_new_rid()`, composes the SID, allocates a gid with winbind, populates a `GROUP_MAP`, and stores it. Builtin alias creation composes from `global_sid_Builtin`, resolves a display name with `lookup_sid()`, optionally allocates a gid, and stores the map.

The Unix group helper functions are script-driven. They read loadparm script settings, substitute `%g` and/or `%u`, execute with `smbrun()`, and flush caches on success. `smb_create_group()` additionally reads a gid from script stdout if available, falling back to `getgrnam()`.

## State And Persistence
This file does not persist mappings directly; it delegates to the backend. It does mutate system state indirectly through configured scripts and can allocate RIDs/gids through passdb/winbind infrastructure. It uses talloc-owned `GROUP_MAP` allocations and moves alias info strings into caller-provided structures.

## Dependencies And Integration Points
It integrates with passdb (`pdb_*` method table expectations), groupdb TDB backend, NSS group lookups, winbind gid allocation, SAM/LSA SID helpers, loadparm script configuration, `smbrun()`, cache flushing, and Samba privilege helpers (`become_root()`/`unbecome_root()` around SID lookup).

## Risks
- Script substitution and execution are high-risk administrative surfaces; correctness relies on loadparm quoting/substitution helpers and trusted configuration.
- `pdb_default_create_alias()` can allocate a RID before gid allocation succeeds, wasting RIDs on failure as the debug message notes.
- `get_domain_group_from_sid()` treats RID 513 specially as "None" with gid -1, which callers must not confuse with a valid Unix-mapped group.
- Backend initialization is global and not designed for multiple backend instances.
- NOP function signatures must remain aligned with passdb expectations; drift can produce subtle callback mismatches.

## Test Signals
Test backend initialization failure, add/update/delete/enum wrappers, domain RID 513 behavior, non-domain SID types, missing Unix gids, alias create/delete/info/set/member flows, builtin alias creation with explicit and allocated gids, and each script helper with success/failure/stdout gid parsing/cache flush behavior.
