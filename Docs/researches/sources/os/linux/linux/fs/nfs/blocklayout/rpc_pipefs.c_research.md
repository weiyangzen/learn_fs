# File Research: sources/os/linux/linux/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose
Provides the rpc_pipefs userspace upcall path for pNFS blocklayout simple-volume device resolution. Kernel code sends encoded block volume signatures to a userspace daemon and receives major/minor device numbers in response.

## Main Responsibilities
- Encode simple block volume signatures for userspace.
- Queue blocklayout device-mount requests on an rpc_pipefs pipe.
- Wait for userspace downcall replies.
- Expose per-network-namespace blocklayout pipe entries under rpc_pipefs.
- Register/unregister pipefs mount event notifiers.

## Key Functions
- `nfs4_encode_simple()` encodes one simple volume and its signatures into XDR-style data.
- `bl_resolve_deviceid()` serializes a `BL_DEVICE_MOUNT` request, queues it to the pipe, waits, and returns `dev_t`.
- `bl_pipe_downcall()` copies a `bl_dev_msg` reply from userspace into per-net state and wakes waiters.
- `bl_pipe_destroy_msg()` wakes the waiter if the upcall is destroyed with an error.
- `nfs4blocklayout_register_sb()` creates the `blocklayout` pipe dentry.
- `rpc_pipefs_event()` handles pipefs mount/unmount by linking or unlinking the pipe.
- `nfs4blocklayout_net_init()` and `_exit()` allocate/destroy per-net pipe data.
- `bl_init_pipefs()` and `bl_cleanup_pipefs()` manage global notifier and pernet registration.

## Control Flow
`bl_resolve_deviceid()` locks `nn->bl_mutex`, builds a pipe message, queues it, sleeps uninterruptibly on `nn->bl_wq`, then validates that userspace returned `BL_DEVICE_REQUEST_PROC`. On success it constructs `MKDEV(reply->major, reply->minor)`.

## Data and Ownership
- Per-net state stores `bl_device_pipe`, `bl_wq`, `bl_mutex`, and `bl_mount_reply`.
- Upcall message data is heap-allocated per request and freed before unlock.
- The single mutex serializes blocklayout device resolution per network namespace.

## Dependencies
Uses SUNRPC rpc_pipefs APIs, net namespace NFS state, blocklayout private message structures, and kernel wait queues.

## Notable Details
- `b->simple.len` is incremented by four bytes to account for a single-volume wrapper before the upcall is built.
- Requests larger than `PAGE_SIZE` are rejected.
- The wait is uninterruptible and has no local timeout; progress depends on userspace or pipe destruction waking the waitqueue.
- Pipe registration is lazy per rpc_pipefs mount and per net namespace.

## Risks and Edge Cases
- One global per-net reply slot means the mutex is essential; any future parallelization must preserve reply association.
- The uninterruptible sleep can hang if neither userspace nor pipe destruction responds.
- `bl_pipe_downcall()` accepts only exact `struct bl_dev_msg` size replies.
- `rpc_pipefs_event()` uses module references to avoid unload during mount/umount notification.

## Integration Points
Called by `dev.c` through `bl_resolve_deviceid()`. The userspace daemon is part of the pNFS blocklayout ecosystem and must understand the `BL_DEVICE_MOUNT` message format.
