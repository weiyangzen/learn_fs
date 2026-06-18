# sources/user-network-fs/fusepy/fuse.py

## Purpose
`fuse.py` is the core fusepy ctypes binding for libfuse. It discovers and loads the native FUSE library, defines platform-specific C structs and callback prototypes, maps libfuse operations into Python methods, provides error translation and context helpers, and exposes the high-level `FUSE`, `Operations`, `FuseOSError`, `LoggingMixIn`, `fuse_get_context()`, and `fuse_exit()` APIs.

## Important APIs, Types, and Functions
- Platform ctypes definitions: `c_timespec`, `c_utimbuf`, `c_stat`, `c_statvfs`, `fuse_file_info`, `fuse_context`, and `fuse_operations`, with Linux/Darwin/FreeBSD/Windows/Cygwin architecture-specific layouts.
- Library loading: `FUSE_LIBRARY_PATH`, `find_library('fuse')`, Darwin iconv loading, WinFsp registry lookup.
- `fuse_get_context()`: returns `(uid, gid, pid)` from native `fuse_get_context`.
- `fuse_exit()`: asks the native FUSE session to exit.
- `FuseOSError(errno)`: convenience exception for errno-returning operations.
- `FUSE.__init__()`: builds argv/options, wraps implemented operations in ctypes callbacks, installs temporary SIGINT default handling, calls `fuse_main_real`, then raises critical exceptions or runtime errors.
- `FUSE` operation methods: decode paths, handle `raw_fi`, marshal read/write buffers, fill `stat`/`statvfs`, xattr buffers, readdir filler, utimens timespecs, and ioctl pointers.
- `Operations`: default high-level filesystem base class with read-only defaults and documented method contracts.
- `LoggingMixIn`: logs operation entry/exit and exceptions.

## Control Flow
At import time the module determines platform and machine, defines exact struct layouts, loads libfuse, and binds `fuse_get_context.restype`. Constructing `FUSE(operations, mountpoint, ...)` builds command-line options from booleans and key/value kwargs, encodes argv, creates a `fuse_operations` struct, and for each operation field checks if the operations object implements it. Implemented functions are wrapped with `_wrapper()` to convert Python exceptions into negative errno returns. `fuse_main_real()` then owns the event loop until unmount/exit. Individual callbacks decode byte paths, translate file handles from `fuse_file_info`, call `operations(op, ...)`, and marshal return values back to C.

## State and Persistence
Module state includes loaded `_libfuse`, detected `_system`/`_machine`, platform type aliases, and logger. `FUSE` instances retain `operations`, `raw_fi`, encoding, nanosecond time mode, and `__critical_exception` during the native event loop; `operations` is deleted afterward to trigger cleanup. Persistent filesystem state is defined by user-provided `Operations` implementations, not the binding itself.

## Dependencies and Integration Points
The module depends on ctypes, native libfuse or WinFsp, OS/platform detection, signal handling, logging, errno/stat conventions, and user operation classes. It is the integration layer used by all high-level fusepy examples in this subset.

## Risks and Edge Cases
The code is ABI-sensitive: incorrect `c_stat`, `c_statvfs`, or `fuse_file_info` layouts for a platform/architecture can cause memory corruption. Import fails if libfuse cannot be found. The Windows branch imports `sys` only inside the branch but uses it there, which is correct only when that branch executes. `_wrapper()` stores critical `BaseException`s and calls `fuse_exit()` because raising through C callbacks can segfault. Most path decoding assumes valid bytes in the configured encoding. `read()` asserts returned data length <= requested size; assertions may be disabled under optimization. Floating-point timestamps are deprecated unless `operations.use_ns` is set. Callback prototypes target FUSE 2.6-era APIs and may not match newer libfuse ABI changes without compatibility layers.

## Test Signals
Tests should cover import/library discovery with `FUSE_LIBRARY_PATH`, struct size/layout smoke tests per supported platform, option normalization, exception-to-errno conversion, path encoding/optional null path handling, `raw_fi` behavior, read/write buffer marshalling, xattr size-query and ERANGE behavior, readdir names plus attr tuples, utimens float vs nanosecond modes, ioctl pointer forwarding, and critical exception shutdown. Integration tests should mount small `Operations` subclasses and exercise common syscalls through the kernel.
