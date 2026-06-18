## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.cc

Purpose: implements administrative filesystem operations around `XrdCl::FileSystem`, primarily locate, query, and stat for a URL.

Important APIs/functions: `FanOut(int&)`, `Query(QueryCode, void*, int)`, `Query(QueryCode, std::string&)`, `Stat(mode_t*, time_t*)`, and `Stat(struct stat&)`.

Control flow: each method first validates the URL through `isOK()`. `FanOut()` performs `DeepLocate()` with `PrefName`, converts each returned address through `XrdNetAddr`, clones the original URL, replaces host/port, and returns a newly allocated URL array. `Query()` sends the path-with-params as an `XrdCl::Buffer`, validates response buffer size, and copies to caller storage or string. `Stat()` calls `Xrd.Stat()`, maps protocol flags to POSIX mode, fills size, inode, blocks, timestamps, and extended permissions when present.

State and persistence: no persistent state. Per-call heap responses (`LocationInfo`, `StatInfo`, `Buffer`) are deleted before return. Errors are stored in the referenced `XrdOucECMsg` and `errno` via `XrdPosixMap::Result()`.

Dependencies/integration: wraps `XrdCl::URL`, `XrdCl::FileSystem`, `XrdCl` response types, `XrdNetAddr`, and `XrdPosixMap`. Used by directory listing, stat-like wrappers, and extended filesystem control paths.

Risks: callers own the `FanOut()` returned array. `Stat.st_blocks` uses `size/512 + size%512`, which overcounts for nonzero remainders by bytes rather than block boolean. Buffer query requires `bsz >= rspSz + 1`; callers must pass enough storage. `strtoll()` inode parsing has no error handling.

Test signals: locate with multiple replicas; invalid URL error message; query response with and without trailing NUL; too-small buffer returns `ERANGE`; stat extended and non-extended format permissions/timestamps.
