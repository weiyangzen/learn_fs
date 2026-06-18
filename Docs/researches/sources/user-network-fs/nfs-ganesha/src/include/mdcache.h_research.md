# sources/user-network-fs/nfs-ganesha/src/include/mdcache.h

## Purpose

`mdcache.h` declares the external control surface for the MDCACHE stackable FSAL. MDCACHE sits above a lower FSAL to provide metadata caching, export stacking, invalidation, and runtime cache policy behavior.

## Important APIs, Types, and Functions

Export lifecycle APIs are `mdcache_fsal_create_export`, `mdcache_fsal_update_export`, and `mdcache_export_uninit`. Package/config APIs are `mdcache_pkginit`, `mdcache_set_param_from_conf`, `mdcache_handle_deleg_transition`, and `init_fds_limit`. The function signatures expose dependencies on FSAL modules, parsed config trees, export handles, Ganesha export objects, config errors, and FSAL upcall vectors.

## Control Flow

During startup or export load, the server initializes the package, parses MDCACHE settings, and creates an MDCACHE export at the top of an FSAL stack. Reloads use `mdcache_fsal_update_export` and delegation transition handling when export policy changes.

## State and Persistence Behavior

The header does not define the cache structures, but it controls process-resident metadata caches and export stack state. Cache entries, file descriptor limits, and delegation modes are runtime state; underlying filesystem persistence remains lower-FSAL-owned.

## Dependencies and Integration Points

It depends on `config.h`, `fsal_types.h`, and `fsal_up.h`. Integration points are FSAL module loading, export manager reloads, upcall invalidation, delegation policy, and startup cleanup on init failure.

## Risks and Test Signals

Risks include cache state surviving failed init, reload transitions leaving stale delegation/cache policy, FD limit misconfiguration, and lower-FSAL operation mismatch. Tests should create/update/unexport MDCACHE-backed exports, inject lower-FSAL errors, verify config parsing bounds, exercise upcall invalidation, and check cleanup after partial initialization.
