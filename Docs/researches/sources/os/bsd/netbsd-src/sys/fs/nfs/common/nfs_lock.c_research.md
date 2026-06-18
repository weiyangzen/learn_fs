# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.c

This file bridges kernel NFS advisory byte-range locking to the userland `rpc.lockd` daemon via a pseudo-device.

Key contents:
- Exports function pointers `nfs_advlock_p = nfs_dolock` and `nfs_reclaim_p`.
- Creates an `nfslock` character device with open, close, read, and write operations.
- Enforces `PRIV_NFS_LOCKD` on open and allows only one opener.
- Maintains a kernel queue of `LOCKD_MSG` requests read by userland lockd.
- `nfs_dolock()` validates lock ranges, extracts NFS vnode info through the mount callback, builds a `LOCKD_MSG`, sends it to lockd, and waits on per-process `nlminfo`.
- Retries unanswered non-unlock requests after 20 seconds.
- `nfslockdans()` receives `lockd_ans` replies, validates version, pid start time, and sequence, then stores the return code and wakes the waiting process.
- `nlminfo_release()` frees process lock metadata.

Important dependencies:
- Uses message structures from `nfs_lock.h`.
- Relies on client mount callbacks from `nfsmount_common`.
- Uses `nlminfo_release_p` hook for process cleanup.

Risks and notes:
- The code deliberately avoids interruptible sleep for pending lock attempts because userland abort handling is incomplete.
- Reply validation reduces but does not eliminate operational complexity around pid reuse and stale answers.
