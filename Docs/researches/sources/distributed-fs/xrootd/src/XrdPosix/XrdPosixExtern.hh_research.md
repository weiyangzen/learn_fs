## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtern.hh

Purpose: declares the C ABI exported XrdPosix wrapper functions and helper probes for use by macro wrappers or preload clients.

Important APIs/types: extern declarations for POSIX wrappers including file, stdio, directory, stat/statfs/statvfs/statx, xattr, and path helpers `XrdPosix_isMyPath` and `XrdPosix_URL`.

Control flow: compile-time only. The header enforces large-file compile flags unless building `XRDPOSIXPRELOAD32`, predeclares structs to avoid symbol conflicts, and wraps declarations in `extern "C"` for C++.

State and persistence: none.

Dependencies/integration: includes `XrdSysStatx.hh`, `dirent.h`, `stdio.h`/`cstdio`, `unistd.h`, `sys/types.h`, and `XrdPosixOsDep.hh`. It must match implementations in `XrdPosix.cc` and preload symbol expectations.

Risks: ABI correctness is critical: signature mismatches break LD-preload interception. Some declarations are platform-conditional; build matrix coverage is needed. The large-file preprocessor guard can fail consumers that include the header before setting required macros.

Test signals: compile C and C++ clients with required flags; symbol export/`nm` checks; 32-bit preload compatibility; platform builds for Linux, macOS, Solaris/BSD variants.
