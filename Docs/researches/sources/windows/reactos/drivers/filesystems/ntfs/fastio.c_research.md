# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fastio.c

Read status: complete file, 148 lines.

This file defines NTFS fast-I/O and cache-manager callback stubs.

Key entry points:
- `NtfsAcqLazyWrite()` and `NtfsRelLazyWrite()` are lazy-writer acquire/release callbacks and are unimplemented.
- `NtfsAcqReadAhead()` and `NtfsRelReadAhead()` are read-ahead acquire/release callbacks and are unimplemented.
- `NtfsFastIoCheckIfPossible()`, `NtfsFastIoRead()`, and `NtfsFastIoWrite()` all return `FALSE`, denying fast I/O.

Important dependencies:
- These callbacks are referenced by global cache-manager callback tables used during `CcInitializeCacheMap()`.

Notable behavior:
- Fast I/O is effectively disabled. All read/write paths must fall back to normal IRP handling.
- Lazy-write and read-ahead callbacks return failure or no-op, so cache-manager integration is minimal.
