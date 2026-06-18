# File Research: sources/os/linux/linux/fs/cachefiles/error_inject.c

## Purpose
Registers a sysctl used to inject CacheFiles read, write, allocation-space, and remove errors during testing.

## Main Elements
- Global state: `cachefiles_error_injection_state`.
- Sysctl table: `/proc/sys/cachefiles/error_injection`, mode `0644`, handled by `proc_douintvec`.
- `cachefiles_register_error_injection()`: registers the sysctl table.
- `cachefiles_unregister_error_injection()`: unregisters it.

## Dependencies And Integration
Enabled by `CONFIG_CACHEFILES_ERROR_INJECTION`. Inline helpers in `internal.h` interpret state bits and return synthetic `-EIO` or `-ENOSPC` to CacheFiles code paths.

## Risk Notes
This is intentionally disruptive and applies while a cache is in service. Production builds without the option compile the helpers to no-op stubs.
