<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh

Purpose: Declares the namespace walker API used to enumerate filesystem directories with XRootD-specific filtering and locking options.

APIs and control flow: `NSEnt` describes returned entries with path, file component, stat data, symlink payload, length, and type. `Index()` is the iterator-like API. `CallBack::isEmpty()` can observe empty directories. Options select returned entry types, stat/link collection, sorted order, recursion, path style, and error skipping.

State and persistence: The walker owns pending directory lists, copied excludes, current directory path storage, and optional lock filename. Returned `NSEnt` lists are owned by the caller.

Dependencies and integration: Forward-declares `XrdOucTList` and `XrdSysError`; includes POSIX stat and fcntl definitions.

Risks and test signals: The API returns raw linked lists and raw pointers into owned path strings, so callers must respect object and entry lifetimes. Tests should validate option combinations, callback behavior, caller deletion of entries, and recursive `Index()` loops until end-of-traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.hh -->
