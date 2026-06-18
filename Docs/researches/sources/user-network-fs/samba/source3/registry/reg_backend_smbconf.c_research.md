# sources/user-network-fs/samba/source3/registry/reg_backend_smbconf.c

## Purpose
`reg_backend_smbconf.c` provides the registry operations for Samba configuration stored below `KEY_SMBCONF`. It is primarily a wrapper around `regdb_ops` with a custom access check requiring disk-operator privilege.

## Important APIs, Types, And Functions
The exported `smbconf_reg_ops` implements fetch/store, create/delete subkey, security descriptor get/set, cache freshness checks, and access checks. `smbconf_reg_access_check()` requires `SEC_PRIV_DISK_OPERATOR` on the provided security token and grants `REG_KEY_ALL` when present. All other operations call through to the same method in `regdb_ops`.

## Control Flow
Registry callers access keys through the dispatcher, which invokes `smbconf_reg_ops` for hooked smbconf paths. Data operations are direct pass-throughs to the registry database. Authorization is the only substantive change: unlike the default security descriptor path, callers without disk-operator privilege are denied before a granted mask is returned.

## State And Persistence
Persistent state lives in the registry database backend. This file does not cache or store anything itself, but it participates in cache invalidation by delegating `subkeys_need_update` and `values_need_update` to `regdb_ops`.

## Dependencies And Integration Points
It depends on `registry.h`, `lib/privileges.h`, `SEC_PRIV_DISK_OPERATOR`, and `regdb_ops`. `reg_init_full.c` hooks it for the full registry, while `reg_init_smbconf.c` can initialize only a selected smbconf key for tools such as `net conf` and loadparm paths.

## Risks And Test Signals
Authorization tests are critical: privileged tokens should receive `REG_KEY_ALL`, while non-privileged tokens fail even for reads. Data operation tests should verify that create, delete, fetch, store, security descriptors, and update checks remain equivalent to `regdb_ops`. Because access checks unconditionally grant all access once the privilege is present, privilege assignment is the security boundary.
