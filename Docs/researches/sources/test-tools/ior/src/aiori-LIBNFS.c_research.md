# sources/test-tools/ior/src/aiori-LIBNFS.c

## Purpose
Implements an IOR backend for libnfs user-space NFS, mounting an RFC2224 URL and translating IOR callbacks to synchronous libnfs operations.

## Important APIs, Types, and Functions
- Global `nfs_context` and `nfs_url` hold the mounted NFS session.
- `Map_IOR_Open_Flags_To_LIBNFS_Flags` maps IOR open flags to POSIX/libnfs flags.
- `LIBNFS_Initialize` creates context, parses `libnfs.url`, and mounts server/path.
- `LIBNFS_Open` uses `nfs_open`; `LIBNFS_Create` uses `nfs_open2` with a mode.
- `LIBNFS_Xfer` seeks with `nfs_lseek`, then uses `nfs_write` or `nfs_read`.
- Metadata wraps `nfs_mkdir2`, `nfs_rmdir`, `nfs_stat64`, `nfs_statvfs64`, `nfs_access`, and `nfs_unlink`.

## Control Flow
Options are allocated by `LIBNFS_GetOptions`. Initialization is a no-op if context or URL already exists. Transfers are seek-then-sequential-operation, returning the backend byte count. Finalize destroys context and parsed URL.

## State and Persistence
Persistent state is on the NFS server. Runtime state is global context/url plus libnfs file handles returned directly as `aiori_fd_t *`. Fsync delegates to `nfs_fsync`; there is no backend-wide sync.

## Dependencies and Integration Points
Requires `<nfsc/libnfs.h>`, `aiori-LIBNFS.h`, IOR utilities, and mdtest callbacks. The header defines only the `libnfs_options_t` URL field used by this implementation.

## Risks and Edge Cases
- No dry-run checks despite storing transfer hints.
- Global context means multiple option sets or parallel backend instances cannot mount different URLs in one process.
- `LIBNFS_Stat` returns `ENOENT` positive for missing paths rather than `-1` with `errno`, which differs from POSIX-style callbacks.
- Transfers do not retry short reads/writes and do not implement fsync-per-write.
- `IOR_EXCL` is not mapped.

## Test Signals
Test URL parsing/mount failures, open/create flag mapping, seek mismatch detection, short transfer reporting, stat/statfs field mapping, mkdir/rmdir with trailing slash, access return conventions, and finalize/reinitialize cycles.
