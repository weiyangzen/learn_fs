# File Research: sources/os/linux/linux/fs/cachefiles/internal.h

## Purpose
Defines CacheFiles internal data structures, state flags, inline helpers, feature stubs, prototypes, error handling macros, and debug/assertion infrastructure shared across the module.

## Main Elements
- Core constants and enums: `CACHEFILES_DIO_BLOCK_SIZE`, `enum cachefiles_content`, and on-demand object states.
- Data structures: `cachefiles_volume`, `cachefiles_ondemand_info`, `cachefiles_object`, `cachefiles_cache`, and `cachefiles_req`.
- State flags: object tmpfile state, cache readiness/death/culling/state-change/on-demand mode, request marks, and closed on-demand IDs.
- Cache-resource helpers: `cachefiles_cres_file()` and `cachefiles_cres_object()`.
- Daemon notification: `cachefiles_state_changed()`.
- Prototypes for cache, daemon, interface, I/O, key, namei, ondemand, security, volume, and xattr files.
- Error-injection stubs and helpers: `cachefiles_inject_read_error()`, `cachefiles_inject_write_error()`, and `cachefiles_inject_remove_error()`.
- On-demand compile-time stubs when `CONFIG_CACHEFILES_ONDEMAND` is disabled.
- Credential override helpers: `cachefiles_begin_secure()` and `cachefiles_end_secure()`.
- Error macros: `cachefiles_io_error()` and `cachefiles_io_error_obj()`.
- Debug and assertion macros.

## Dependencies And Integration
This header is the module's internal contract and directly ties CacheFiles to FS-Cache, xarrays, credentials/security, tracepoints, and the user ABI in `<linux/cachefiles.h>`.

## Risk Notes
The macros can mark a cache dead and flush on-demand requests from many call sites, so error paths have broad side effects. On-demand stubs must preserve behavior when the feature is disabled. Assertion macros call `BUG()` in active builds, making invariant failures fatal.
