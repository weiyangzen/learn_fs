# File Research: sources/os/linux/linux-stable/fs/cachefiles/error_inject.c

This optional file implements sysctl-backed error injection for CacheFiles when `CONFIG_CACHEFILES_ERROR_INJECTION` is enabled.

Main state:
- `cachefiles_error_injection_state`: global unsigned integer controlling injected failures.

Sysctl:
- Registers `/proc/sys/cachefiles/error_injection` with mode `0644` and `proc_douintvec`.
- `cachefiles_register_error_injection()` registers the sysctl table and returns `-ENOMEM` if registration fails.
- `cachefiles_unregister_error_injection()` unregisters it.

Consumers:
- Inline helpers in `internal.h` interpret the state:
  - read/remove errors return `-EIO` when bit 1 is set.
  - write errors return `-EIO` when bit 1 is set or `-ENOSPC` when bit 0 is set.

Purpose:
- Provides a controlled way to exercise CacheFiles error paths for VFS operations, xattr updates, lookup, read/write, truncate, unlink, rename, and fallocate paths.
