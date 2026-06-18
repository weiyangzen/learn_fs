# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusebuf.c

Purpose: Allocates, initializes, queues, waits for, and frees FUSE request buffers.

Key behavior:
- `fb_setup()` allocates a zeroed `struct fusebuf` from `fusefs_fbuf_pool`, sets length, UUID, operation type, inode, thread/user/group IDs, umask, and optional payload buffer.
- `fb_queue()` queues the request to the FUSE device and sleeps indefinitely until the daemon response or cleanup wakes it.
- `fb_delete()` frees payload memory and returns the request object to the pool.

Design note:
- Blocking is intentionally non-interruptible and timeout-free, matching regular VFS syscall behavior and relying on daemon termination/device cleanup to wake stalled callers.
