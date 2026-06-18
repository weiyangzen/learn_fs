## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.hh

Purpose: defines platform-specific native POSIX symbol names, return types, argument lists, and the `XrdPosixLinkage` function-pointer table.

Important APIs/types: `Symb_*`, `Retv_*`, and `Args_*` macros for access, open, stat variants, stdio, directory, xattr, and I/O calls; class `XrdPosixLinkage` with function-pointer members, `Init`, `Load_Error`, private `Resolve`, and `Missing`.

Control flow: constructor initializes the table by resolving symbols. Wrappers use table entries for local passthrough. Macro definitions account for Linux `_STAT_VER` symbols, macOS 64-bit aliasing, and optional `statx`.

State and persistence: one object holds resolved pointers and `Done` initialization flag. No persistence.

Dependencies/integration: includes POSIX headers, `XrdPosixOsDep.hh`, `XrdPosixXrootd.hh`, platform/statx helpers. Must remain consistent with `XrdPosixLinkage.cc` and system ABI.

Risks: `Args_Openat`/`Args_Openat64` macros omit the `dirfd` parameter shape expected by POSIX `openat`; this warrants platform build verification even if not used in `Resolve()` currently. Conditional macro complexity can hide ABI drift. Function pointer varargs are inherently hard to type-check.

Test signals: compile with strict warnings on each supported OS; compare resolved symbol names using `dlsym`; run local passthrough operations with `_FILE_OFFSET_BITS=64`; validate stat ABI variants.
