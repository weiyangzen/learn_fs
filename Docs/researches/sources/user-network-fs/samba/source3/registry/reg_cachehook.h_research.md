# sources/user-network-fs/samba/source3/registry/reg_cachehook.h

## Purpose
`reg_cachehook.h` declares the hook-cache interface used to register and resolve registry backends by key path.

## Important APIs, Types, And Functions
The header exposes `reghook_cache_init()`, `reghook_cache_add(const char *keyname, struct registry_ops *ops)`, `reghook_cache_find(const char *keyname)`, and `reghook_dump_cache(int debuglevel)`. It forward-relies on `WERROR` and `struct registry_ops` being visible through includers such as `registry.h`.

## Control Flow
Callers initialize the cache, add one or more key-to-ops mappings, then resolve key names during registry open/dispatch. The dump function is diagnostic and has no return value.

## State And Persistence
The header declares no data. Its implementation manages an in-memory process-global path tree and does not persist the hook map.

## Dependencies And Integration Points
Included by registry initialization modules and any code that needs hook lookup. It forms a small public boundary over `reg_cachehook.c` while hiding the `sorted_tree` implementation.

## Risks And Test Signals
The header has no direct include of `registry.h`, so include-order assumptions matter. Compile tests should cover consumers that include it after the necessary type definitions. API tests should focus on the implementation's invalid-parameter and default-backend behavior.
