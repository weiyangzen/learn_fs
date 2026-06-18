# sources/user-network-fs/samba/source3/registry/reg_init_smbconf.c

## Purpose
`reg_init_smbconf.c` initializes just the smbconf portion of the registry. It is intended for paths that do not need the full registry backend set, such as `net conf` and loadparm-related use.

## Important APIs, Types, And Functions
`registry_init_smbconf(const char *keyname)` defaults a null key to `KEY_SMBCONF`, calls `registry_init_common()`, ensures the target key exists through `init_registry_key()`, and registers `smbconf_reg_ops` for that key with `reghook_cache_add()`.

## Control Flow
The function performs common initialization first. If key initialization fails, it logs a level-1 error and returns. If hook registration fails, it logs a separate error. It closes the registry database before returning in all paths after common initialization.

## State And Persistence
It creates or verifies the persistent smbconf registry key and adds a process-local hook-cache mapping to `smbconf_reg_ops`. It does not register unrelated virtual backends.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_cachehook.h`, `reg_backend_db.h`, `reg_init_basic.h`, and `smbconf_reg_ops`. It complements `registry_init_full()` with a narrower setup surface.

## Risks And Test Signals
Tests should cover null-key defaulting, custom key names, failure from common init, failure from key creation, and failure from hook-cache insertion. Access-control behavior should be tested through the smbconf backend after this initializer has registered it.
