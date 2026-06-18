# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephPosix.cc

Purpose: provides the POSIX-like shim that backs the Ceph OSS and xattr plugins. It maps path syntax, synthetic file descriptors, reads/writes, xattrs, stats, directory iteration, and connection pooling onto librados and libradosstriper APIs.

Important APIs and state: global vectors `g_radosStripers`, `g_ioCtx`, and `g_cluster` hold per-pool-index connection resources; `g_fds` maps synthetic fds to `CephFileRef`; `g_filesOpenForWrite` tracks in-progress writes for stat behavior; mutexes protect connection and fd maps. Path parsing uses defaults from `g_defaultParams` and optional `XrdOucEnv` entries, with optional name translation through `g_namelib`.

Control flow: `ceph_posix_open()` parses the file, obtains a striper, stats existence, adjusts read layout from object xattrs when possible, and inserts a fd for read or write. Reads can use striper APIs or direct RADOS object reads via `bulkAioRead`; direct reads only support `nbStripes == 1` and fall back elsewhere. Writes use striper write/aio_write and maintain counters. AIO callbacks update stats before invoking XRootD callbacks. Stat methods synthesize POSIX fields; xattr methods call striper get/set/list/remove xattrs; space methods use cluster and pool stats; unlink removes a striper lock xattr on `-EBUSY` and retries. Directory listing exposes top-level objects with `.0000000000000000` suffixes stripped.

State and persistence: persistent state is Ceph object content, xattrs, and pool stats. Process state includes open fds, counters, connection pools, layout defaults, and pending AIO bookkeeping.

Dependencies and integration: depends on librados, libradosstriper, XRootD AIO/OSS/platform types, `XrdCephBulkAioRead`, and checksum/xattr users through exported functions in `XrdCephPosix.hh`.

Risks and test signals: critical tests include multi-connection initialization, concurrent open/close/read/write, AIO completion after close assumptions, direct-read fallback, xattr list allocation/free, path parsing, name translation, pool stats, and unlink lock retry. Notable risks include synthetic fd wraparound, borrowed `CephFileRef*` lifetime, `ceph_posix_internal_listxattrs()` copying the name with `Vlen+1` instead of name length, and `ceph_posix_freexattrlist()` freeing `aPL->Name` even though entries are allocated as one block with embedded names.
