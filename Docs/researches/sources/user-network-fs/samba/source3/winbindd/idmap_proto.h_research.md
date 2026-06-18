# sources/user-network-fs/samba/source3/winbindd/idmap_proto.h

## Purpose
This generated-style prototype header exposes idmap subsystem functions and backend init entry points used by winbindd source files. It centralizes declarations for idmap core, built-in backends, utility helpers, and LDAP batch sizing.

## Important APIs, Types, And Functions
Core declarations include `idmap_is_offline`, `smb_register_idmap`, `idmap_close`, `idmap_allocate_uid`, `idmap_allocate_gid`, `idmap_backend_unixids_to_sids`, and `idmap_find_domain`. Backend init declarations include `idmap_nss_init`, `idmap_passdb_init`, `idmap_tdb_init`, and `idmap_ad_nss_init`. Utility declarations include range checking, map lookup by ID/SID, secret fetching, and `id_map_ptrs_init`. `IDMAP_LDAP_MAX_IDS` is defined as 30.

## Control Flow
The header does not implement control flow. Its structure groups declarations by originating file comments, which helps link backend modules to the core idmap API.

## State And Persistence
No state is held here. The declared functions touch global idmap registry state, backend private data, secrets, TDB, LDAP, and caches depending on implementation.

## Dependencies And Integration
It assumes `idmap.h` has declared `struct idmap_domain`, `struct id_map`, `struct unixid`, `struct dom_sid`, and `struct idmap_methods`. It is included indirectly by `source3/include/idmap.h`.

## Risks And Test Signals
Build tests are the main signal: stale prototypes will surface as incompatible declarations or missing symbols. `IDMAP_LDAP_MAX_IDS` affects LDAP batching in multiple files, so behavioral tests should include batch sizes of 0, 1, 30, and 31.
