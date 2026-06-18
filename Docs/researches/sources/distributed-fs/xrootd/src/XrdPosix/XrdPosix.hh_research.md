## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.hh

Purpose: public include that redirects common POSIX and stdio function names to the XRootD-aware `XrdPosix_*` wrappers. It is intended for source-level interposition where platform-specific wrapper mechanisms are unreliable.

Important APIs/types: includes `XrdPosixExtern.hh` and defines macros for `access`, `chdir`, `close`, directory functions, `open`, `openat`, read/write variants, stat functions, xattr functions, and `statx`.

Control flow: there is no runtime flow; inclusion rewrites subsequent source references through preprocessor macros. `open` and `openat` are macro aliases without argument lists so varargs survive. `rewinddir` is explicitly undefined first to handle prior macro definitions.

State and persistence: no state. It changes compile-time symbol binding for translation units that include it.

Dependencies/integration: depends on `dirent.h` and the ABI-safe declarations in `XrdPosixExtern.hh`. It integrates with both preload-style exported symbols and direct source inclusion.

Risks: macro interposition is broad and can unexpectedly affect third-party headers included afterward. `lstat` is mapped to `XrdPosix_Stat` rather than `XrdPosix_Lstat`, which intentionally follows the same semantics as the implementation but is surprising. Missing coverage for functions not listed here will bypass XRootD dispatch.

Test signals: compile representative clients with this header; verify varargs calls still compile; confirm local and remote behavior for `lstat`, `open`, `statx`, and xattrs; test inclusion order with system headers.
