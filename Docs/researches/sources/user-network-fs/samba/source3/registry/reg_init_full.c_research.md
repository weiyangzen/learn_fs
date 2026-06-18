# sources/user-network-fs/samba/source3/registry/reg_init_full.c

## Purpose
`reg_init_full.c` initializes the registry with all available source3 virtual backends and default database-backed paths.

## Important APIs, Types, And Functions
It declares external `registry_ops` tables for printing, eventlog, shares, smbconf, netlogon parameters, product options, TCP/IP parameters, performance text, current version, perflib, and the default database. `struct registry_hook` pairs a key name with an ops table. `reg_hooks[]` is the authoritative registration list. `registry_init_full()` installs those hooks into the hook cache.

## Control Flow
`registry_init_full()` calls `registry_init_common()`, loops over `reg_hooks[]`, and calls `reghook_cache_add()` for each entry. If any hook insertion fails, initialization stops. At high debug levels it dumps the hook tree. The function closes the registry database before returning.

## State And Persistence
Persistent base registry data is initialized by the shared common path. The full initializer populates only the process-local hook cache; the hook map itself is not persisted.

## Dependencies And Integration Points
It depends on the backend ops symbols from multiple registry modules and on key constants from `registry.h`. It is the central integration point that determines which backend owns which registry subtree.

## Risks And Test Signals
Hook ordering matters for prefix matching, so tests should verify the selected backend for each registered key and representative child paths. Failure tests should cover hook-cache add errors and common-init errors. Build/link tests are also important because this file references many external backend symbols.
