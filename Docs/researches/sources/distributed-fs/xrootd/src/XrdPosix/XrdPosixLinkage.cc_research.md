## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.cc

Purpose: implements the native Unix callout vector for interposed POSIX functions, resolving real libc symbols with `dlsym(RTLD_NEXT)` and providing failure stubs.

Important APIs/functions: global `XrdPosixLinkage Xunix`; `Resolve()`, `Load_Error()`, `Missing()`, `LOOKUP_UNIX` macro, and many `Xrd_U_*` unresolved stubs.

Control flow: static construction calls `Init()`/`Resolve()`. Each symbol pointer is loaded from the next shared object; missing symbols are replaced by a stub and recorded. Wrapper code calls `Xunix.<Function>()` for local paths. `Load_Error()` reports unresolved calls through native write paths when available, sets `errno=ELIBACC`, and returns a failure value. If `XRDPOSIX_REPORT` is set, all missing symbols are printed.

State and persistence: stores function pointers in the global `Xunix` object and a process-local linked list of missing symbol names. No durable state.

Dependencies/integration: depends on `dlfcn.h`, platform linker headers, `XrdPosixLinkage.hh`, libc, and OS-specific symbol names. It is foundational for preload safety.

Risks: symbol signatures in the header must exactly match platform libc. Fallback report string in `Missing()` appears to omit a closing quote/paren formatting. Some stubs abort for void directory functions. Duplicate `LOOKUP_UNIX(Fsync)` appears in `Resolve()`. Static initialization order matters.

Test signals: LD_PRELOAD smoke tests; `XRDPOSIX_REPORT` missing-symbol output; platform builds for Linux/macOS/Solaris; local passthrough for every wrapper; unresolved symbol failure behavior.
