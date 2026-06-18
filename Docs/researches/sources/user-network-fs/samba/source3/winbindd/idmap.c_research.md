# sources/user-network-fs/samba/source3/winbindd/idmap.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap.c` implements the winbind idmap backend registry, idmap domain initialization/selection, configuration accessors, allocator wrappers, and Unix-ID-to-SID dispatch. It is the central glue between winbind callers and pluggable idmap modules. The source was read as a complete 632-line file.

## Important APIs, Types, and Functions

Important functions are `lp_scan_idmap_domains`, `idmap_init`, `smb_register_idmap`, `idmap_find_domain`, `idmap_find_domain_with_sid`, `idmap_close`, `idmap_allocate_uid`, `idmap_allocate_gid`, `idmap_backend_unixids_to_sids`, and config helpers `idmap_config_const_string`, `idmap_config_bool`, `idmap_config_int`, `idmap_config_string_list`, `domain_has_idmap_config`. Important static state includes backend list `backends`, `default_idmap_domain`, `passdb_idmap_domain`, `idmap_domains`, and `num_domains`.

## Control Flow

Backends register with `smb_register_idmap`. `idmap_init` runs static backend initialization once, creates the default `*` domain unless passdb owns everything else, creates a passdb domain for the local SAM, allocates the named-domain list, and scans parametric `idmap config DOMAIN : backend` settings. Domain creation loads/probes the requested backend, parses range/read-only options, and calls backend `init`.

## State and Persistence Behavior

This file owns process-global in-memory registry/domain state. It reads idmap configuration from loadparm but does not persist mappings itself; persistence is delegated to backend methods.

## Dependencies and Integration Points

It integrates with static idmap module declarations, dynamic module probing, passdb SID ownership, Samba loadparm parametric options, winbind offline state, and backend method tables (`init`, `allocate_id`, `unixids_to_sids`, `sids_to_unixids`). `idmap_find_domain_with_sid` routes passdb-owned SIDs to the passdb backend.

## Risks and Edge Cases

Initialization is guarded by a static bool and uses globals, so lifecycle and reinitialization must be careful. Range parsing accepts missing/invalid ranges only when `check_range` is false. `domain_has_idmap_config` checks initialized domains and loadparm fallback. Backend registration rejects version mismatch and duplicate names; missing modules fail domain creation. `idmap_close` frees domains but does not reset the static initialized flag.

## Test Signals

Tests should cover backend registration version/name validation, default/passdb/named domain selection, dynamic module probing failures, range parsing, read-only option handling, domain scanning, passdb SID routing, allocator wrappers, and close/reinitialize behavior.
