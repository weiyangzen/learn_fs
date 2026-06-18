# sources/storage-engines/wiredtiger/src/os_common/os_errno.c

## Purpose
Provides portable error-code normalization and stringification for WiredTiger and system errors.

## Important APIs, Types, and Functions
`__wt_errno` returns `errno` or `WT_ERROR` if errno is zero. `__wt_strerror` returns a WiredTiger constant string when available or formats a generic numeric error string into a caller buffer or the session error buffer. `__wt_ext_map_windows_error` exposes Windows-to-POSIX error mapping to extensions on Windows and panics if called on non-Windows builds.

## Control Flow
Error string lookup first checks WiredTiger-specific constants, then tries the provided buffer, then the session buffer, and finally a fixed fallback string. The Windows mapping wrapper compiles to the real mapper only on `_WIN32`; otherwise it treats use as an API misuse panic.

## State and Persistence Behavior
There is no persistence. `__wt_strerror` may update `session->err`, which is per-session transient diagnostic state.

## Dependencies and Integration Points
The file depends on `errno`, `__wt_wiredtiger_error`, `__wt_snprintf`, `__wt_buf_fmt`, and extension API ABI. It is used by nearly every OS wrapper and error-reporting path.

## Risks and Edge Cases
`__wt_errno` hides missing errno by returning a generic error, which is safer than success but less precise. `__wt_strerror` does not call libc `strerror`; unknown POSIX errors are reported numerically. Non-Windows extension calls to map Windows errors panic by design.

## Test Signals
Tests should cover WiredTiger error constants, unknown numeric errors with caller and session buffers, `errno == 0` normalization, and platform-specific extension mapping behavior.
