# sources/user-network-fs/samba/source3/registry/reg_init_basic.c

## Purpose
`reg_init_basic.c` implements common registry initialization and a basic initializer that sets up the database and hook cache without installing the full set of virtual backends.

## Important APIs, Types, And Functions
`registry_init_common()` calls `regdb_init()`, `reghook_cache_init()`, and `init_registry_data()`, returning a `WERROR`. `registry_init_basic()` logs, calls the common initializer, closes the registry database with `regdb_close()`, and returns the result.

## Control Flow
Initialization fails fast for database and hook-cache setup. Registry data initialization errors are logged and returned through `werr`. The basic initializer always closes the database after common initialization so later processes or callers can open it as needed.

## State And Persistence
This code initializes persistent registry database content through `init_registry_data()` and initializes the in-memory hook cache. It does not itself register virtual backends beyond the cache default established by `reghook_cache_init()`.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_init_basic.h`, `reg_cachehook.h`, and `reg_backend_db.h`. Full and smbconf-specific initialization reuse `registry_init_common()`.

## Risks And Test Signals
Tests should cover failure propagation from `regdb_init()` and `reghook_cache_init()`, database closure after basic init, and idempotency when called more than once. Initialization should also be tested against an empty registry database to verify built-in keys and values are created.
