# File Research: sources/os/linux/linux/fs/nfsd/trace.h

`trace.h` defines the Linux tracepoint surface for the in-kernel NFS server (`TRACE_SYSTEM nfsd`). It is observability infrastructure, not request processing logic. It includes SUNRPC/NFS trace helpers plus local NFSD headers for exports, filehandles, state, filecache, VFS, and duplicate-reply cache types.

Major trace families:
- XDR failures: `nfsd_garbage_args_err`, `nfsd_cant_encode_err`.
- Dynamic thread pool events: start, kill, trylock failure, with net namespace, pool id, and thread limits.
- NFSv4 compound operation lifecycle: compound start, status, decode errors, op/encode errors.
- Filehandle/export lookup: `nfsd_fh_verify`, `nfsd_fh_verify_err`, export key/name update/find events.
- I/O: read/write/commit start, splice/vector/direct paths, I/O completion, and read/write error events.
- State management: stateid, state sequence id, stateid revocation, clientid lifecycle, grace period, session slot and sequence status.
- File cache: allocation, acquisition, open/opened, cache hits, fsnotify events, LRU/GC/shrinker activity, close.
- DRC: duplicate reply cache found and checksum mismatch.
- NFSv4 callback channel: setup, state transitions, queue/restart/destroy, sequence status, recall, notify-lock, offload, recall-any and callback completion.
- Control plane: procfs/control operations such as unlock, filehandle, threads, pool threads, protocol versions, ports, block size, grace time, recoverydir, and fh key setting.
- Server-side copy and pNFS: inter/intra/async copy, async completion/cancel, VFS clone errors, pNFS fence errors.
- NFSD VFS entry points: setattr, lookup, create, symlink, link, unlink, rename, readdir, getattr/statfs.

Notable implementation patterns:
- Shared macros (`NFSD_TRACE_PROC_CALL_FIELDS`, `NFSD_TRACE_PROC_RES_FIELDS`) standardize xid, net namespace inode, server/client sockaddr, and status capture.
- Display helpers translate internal bitmasks such as `NFSD_MAY_*`, file types, slot flags, callback state/opcode, auth flavor, DRC result, and stateid status into readable trace output.
- Several tracepoints deliberately avoid dereferencing potentially unsafe pointers in print paths and record hashes or raw pointer values instead.
- Conditional trace events suppress noise when request context is unavailable or there is no error/status flag.

This file is central for debugging NFSD request flow, state lifetime, file cache behavior, VFS operations, server-side copy, and callback behavior without changing NFSD execution logic.
