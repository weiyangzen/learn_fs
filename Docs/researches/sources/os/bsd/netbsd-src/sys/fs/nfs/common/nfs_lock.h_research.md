# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.h

This header defines the kernel/userland lockd protocol structures.

Key contents:
- Defines `_PATH_NFSLCKDEV` as `nfslock`.
- `struct lockd_msg_ident` identifies requests by pid, pid start time, and message sequence.
- `LOCKD_MSG_VERSION` is 3.
- `LOCKD_MSG` includes flock data, wait/getlk flags, server address, NFS version flag, file handle length/data, and credentials.
- `LOCKD_ANS_VERSION` is 1.
- `struct lockd_ans` carries the matched identifier, errno, and optional `F_GETLK` pid result.
- Kernel declarations expose `nfs_dolock()`, `nfs_advlock_p`, and `nfs_reclaim_p`.

Important dependencies:
- Uses `NFSX_V3FHMAX` for maximum file handle storage.
- Paired directly with `nfs_lock.c`.

Risks and notes:
- Any structure layout change requires version bumps because userland lockd consumes these records.
