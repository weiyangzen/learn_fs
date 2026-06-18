# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_ipc.c

Shared permission helper for System V IPC objects.

Main function:
- `ipcperm(struct ucred *cred, struct ipc_perm *perm, int mode)`.

Behavior:
- For `IPC_M`, permits root, the owner uid, or creator uid; otherwise returns `EPERM`.
- For read/write-style checks, calls `vaccess()` twice: once against current owner uid/gid and once against creator uid/gid.
- Returns success if either access check passes; otherwise returns `EACCES`.

Design note:
- Reuses vnode access semantics (`vaccess(VNON, ...)`) for IPC permission-bit checks even though the target is not a vnode.

Filesystem/storage relevance:
- Not filesystem logic, but it reuses VFS permission-check machinery and is a common authorization dependency for the message queue, semaphore, and shared-memory implementations in this group.
