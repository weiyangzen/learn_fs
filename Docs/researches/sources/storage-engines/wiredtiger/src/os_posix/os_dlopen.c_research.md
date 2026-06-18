# sources/storage-engines/wiredtiger/src/os_posix/os_dlopen.c

## Purpose
Wraps POSIX dynamic library loading, symbol lookup, and closing for WiredTiger extensions.

## Important APIs, Types, and Functions
Functions are `__wt_dlopen`, `__wt_dlsym`, and `__wt_dlclose`. The handle type is `WT_DLH`, which stores a library name and `dlopen` handle.

## Control Flow
Open allocates a `WT_DLH`, stores `path` or `"local"` as the name, and calls `dlopen(path, RTLD_LAZY)`. Symbol lookup clears the output pointer, calls `dlsym`, returns success with NULL when missing and `fail` is false, or reports an error when `fail` is true. Close calls `dlclose` except on FreeBSD, then frees the name and handle wrapper.

## State and Persistence Behavior
Loaded dynamic library handles are process state only. No database files are modified.

## Dependencies and Integration Points
This file supports extension loading and local extension symbol lookup. It depends on `dlopen`, `dlsym`, `dlclose`, `dlerror`, allocation, and error reporting.

## Risks and Edge Cases
FreeBSD intentionally skips `dlclose` to avoid crashes in `__cxa_finalize`, leaking resources until process exit. `dlopen(NULL)` is represented as `"local"` for diagnostics. Missing optional symbols are not errors when `fail` is false.

## Test Signals
Extension tests should cover loading shared libraries, local symbol lookup, missing required and optional symbols, close behavior, and FreeBSD-specific no-close behavior.
