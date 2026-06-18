# sources/user-network-fs/samba/source3/lib/smbconf/smbconf_reg.c

## Purpose
This file implements the read-write registry backend for libsmbconf. It maps smbconf services and parameters to registry keys and values under the SMB configuration registry path.

## Important APIs, Types, And Functions
`struct reg_private_data` stores the base registry key and whether this backend opened the registry database. `smbconf_reg_parameter_is_valid()` filters loadparm-valid parameters and forbids state/lock/config backend/include internals. Helper functions open/create service keys, test value existence, set `REG_SZ` parameters with canonicalized names/values, set `REG_MULTI_SZ` include lists, format registry values back to strings, enumerate values, and delete values. The exported initializer is `smbconf_init_reg()`, which calls `smbconf_init_internal()` with `smbconf_ops_reg`.

## Control Flow
Initialization creates an admin registry token, initializes the smbconf registry path, opens regdb, and opens the base key. Operations implement the `smbconf_ops` table: open/close, change-sequence number, drop/reset subtree, enumerate share names with `global` first, create/get/delete shares, set/get/delete parameters, get/set/delete includes, and transaction start/commit/cancel. Service `NULL` means the base/global key for several helpers; non-NULL service names map to subkeys. `get_share()` preserves actual registry key case by enumerating base subkeys.

## State And Persistence
Persistent configuration lives in the Samba registry database. Ordinary parameters are stored as `REG_SZ`; include lists are stored internally as `REG_MULTI_SZ` under the special value name `includes` but are exposed as repeated `include` parameters. The backend tracks open/closed state in the context private data and uses regdb sequence numbers as CSNs.

## Dependencies And Integration Points
It depends on source3 registry APIs, registry database backend, admin token creation, loadparm parameter validation/canonicalization, smbconf private operation contracts, and clustering/loadparm checks for messaging needs. It is the writable config backend for tools and Python bindings.

## Risks And Test Signals
Risk areas are registry permission/token assumptions, reserved parameter filtering, canonicalization/value validation differences from text backend, deleting while enumerating values, treating registry open state as context-local over a process-global regdb, CTDB registry messaging requirements, and fallback error mapping that often collapses registry errors to generic smbconf errors. Tests should cover parameter validation, global-only parameter rejection in services, include round trips, share create/get/delete/drop, transaction commit/cancel, CSN changes, clustered `requires_messaging`, and Python/C initialization using default and explicit paths.
