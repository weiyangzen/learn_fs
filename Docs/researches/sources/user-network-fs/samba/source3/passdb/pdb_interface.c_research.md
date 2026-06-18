# sources/user-network-fs/samba/source3/passdb/pdb_interface.c

## Purpose

`pdb_interface.c` is the passdb backend dispatcher and default implementation provider. It registers passdb modules, initializes the configured backend, exposes global wrapper functions for account/group/alias/trust/secret operations, manages selected caches, maps SIDs and Unix IDs, and fills a `struct pdb_methods` table with default behavior that modules can override.

## Important APIs And Functions

Backend management includes `smb_register_passdb()`, `pdb_find_backend_entry()`, `pdb_get_backends()`, `make_pdb_method_name()`, `initialize_password_db()`, `pdb_get_tevent_context()`, and private method-cache helpers. Account, group, alias, policy, ID, search, trust, UPN, responsibility, and secret wrappers dispatch through the active `pdb_methods` table. `make_pdb_method()` initializes that table with default implementations for accounts, groups, aliases, policies, ID mapping, searches, trusts, trusted domains, hints, secrets, UPN suffixes, and responsibility checks.

## Control Flow And State

Backend initialization is lazy. `make_pdb_method_name()` parses `backend[:location]`, searches registered built-ins, optionally probes a plugin, then calls the backend init function. `pdb_get_methods_reload()` caches the active singleton and recreates it on reload. `pdb_getsampwnam()` delegates to the backend, tries to unlock expired autolocks, copies the account into a SID-keyed memcache, and returns success. `pdb_getsampwsid()` handles guest RID 501 specially, checks the SID is in the global SAM, uses the SID cache when possible, otherwise calls the backend, then tries unlock. Updates and deletes flush or delete cache entries and user deletion sends an ID-cache delete message.

Default user creation locates or creates a Unix account via configured add-user/add-machine scripts, flushes NSS caches, builds a `samu`, allocates a RID, disables the account until a password is set, and calls `add_sam_account()`. Default group and membership methods bridge Samba group mapping to Unix group commands. ID mapping defaults check local SAM, Unix Users/Groups synthetic SID spaces, BUILTIN/well-known aliases, then fail. `pdb_new_rid()` requires store-RID capability and retries backend allocations until `lookup_global_sam_rid()` confirms the RID is unused. Search APIs lazily cache `samr_displayentry` rows and close backend searches through a destructor.

## Persistence Behavior

Persistence is backend-dependent through `struct pdb_methods`. This file mutates global singleton state (`backends`, active `pdb_methods`, `pdb_tevent_ctx`) and memory caches. It can trigger external Unix account/group scripts and NSS cache flushes. Account policies are read/written through backend methods while elevated with `become_root()`. Trust defaults persist through secrets helper functions; secret defaults persist through LSA secret APIs.

## Dependencies And Integration Points

The file integrates generated SAMR/DRS/idmap NDR types, memcache, winbind environment controls, loadparm, messaging, server IDs, Unix passwd/group helpers, group mapping, idmap cache, secrets, and global context access. It is the primary public C API layer between Samba services/RPC code and concrete passdb modules such as tdbsam, smbpasswd, ldap, or secrets-backed implementations.

## Risks And Test Signals

Global singleton backend state makes reload and plugin registration order important. External scripts can have side effects outside passdb and are only partially verified. Cache correctness depends on flushing on every update/rename/delete path. `lookup_global_sam_rid()` appears to treat the allocated `sam_account` pointer as a found user even after lookup failure, which is a defect signal because the pointer exists regardless of backend result. Tests should cover backend registration and plugin load failures, reload freeing private data, account cache behavior, autolock expiry update, guest SID lookup, script branches and root protection, group membership verification, SID/ID mappings, RID allocation collision retries, search pagination/destructor behavior, trusted-domain default packing/unpacking, LSA secret delegation, and method table defaults.
