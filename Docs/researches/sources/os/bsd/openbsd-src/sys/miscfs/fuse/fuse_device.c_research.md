# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_device.c

Purpose: Implements the `/dev/fuse` character device side of OpenBSD FUSE request delivery and daemon response handling.

Key behavior:
- `struct fuse_d` tracks a per-device rwlock, refcount, mounted `fusefs_mnt`, unit number, inbound request queue, wait-for-response queue, and read kqueue list.
- `fuseopen()` creates one open device instance per unit and rejects exclusive or duplicate opens.
- `fuseclose()` cleans queued messages, marks the session dead, detaches the mount, removes the device from the global list, finalizes references, and frees state.
- `fuse_device_queue_fbuf()` queues kernel requests for userspace, wakes readers, and signals kqueue readers.
- `fuseread()` blocks or returns `EAGAIN` until a queued request exists, copies a complete `fusebuf` header/operation payload to userspace without exposing kernel queue pointers, then moves the request to the wait queue.
- `fusewrite()` reads a userspace response, validates length and matching UUID, updates the waiting `fusebuf`, copies response data, handles `FBT_INIT` and `FBT_DESTROY`, removes the wait entry, and wakes the sleeping VFS caller.
- `fuse_device_cleanup()` marks queued and waiting requests with `ENXIO` and wakes blocked VFS callers.
- `fusekqfilter()` supports read readiness on pending inbound requests and always-writable behavior through `seltrue_kqfilter()`.

Concurrency and safety:
- Uses rwlocks for request queue/kqueue protection and refcounts for lifetime.
- Refuses oversized or malformed responses and avoids leaking kernel pointers to userspace.
