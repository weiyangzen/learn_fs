# sources/user-network-fs/samba/source3/registry/reg_cachehook.c

## Purpose
`reg_cachehook.c` owns the registry hook cache: a path tree mapping registry key prefixes to `struct registry_ops` implementations. It lets the frontend find the correct backend for any registry key while falling back to the default database backend.

## Important APIs, Types, And Functions
`reghook_cache_init()` initializes the global `cache_tree` with `regdb_ops` as the default. `reghook_cache_add()` converts a key name into the path-tree format and inserts an ops pointer. `reghook_cache_find()` resolves a key name to the best matching ops pointer. `reghook_dump_cache()` prints the tree for diagnostics. The helper `keyname_to_path()` prepends a backslash because the path-tree implementation expects that shape.

## Control Flow
Initialization is idempotent: if `cache_tree` already exists, `reghook_cache_init()` returns success. Full or partial registry init calls `reghook_cache_add()` for each virtual backend. Later, registry open paths call `reghook_cache_find()` to select operations for a key handle.

## State And Persistence
The only state is the process-global `static struct sorted_tree *cache_tree`. It is in-memory and not persisted. Stored registry values remain in the backend selected by each ops pointer, usually `regdb_ops`.

## Dependencies And Integration Points
The file depends on `adt_tree.h` for `pathtree_init()`, `pathtree_add()`, `pathtree_find()`, and `pathtree_print_keys()`, plus `registry.h` and `reg_cachehook.h`. It is used by `reg_init_basic.c`, `reg_init_full.c`, and `reg_init_smbconf.c`.

## Risks And Test Signals
The cache has global lifetime and no explicit teardown in this file, so tests should isolate process state or reinitialize carefully. `reghook_cache_add()` assumes initialization has happened; direct calls before `reghook_cache_init()` risk null tree use. Tests should verify default fallback, longest-prefix matching, invalid parameter returns, duplicate/repeated initialization, and debug dump stability.
