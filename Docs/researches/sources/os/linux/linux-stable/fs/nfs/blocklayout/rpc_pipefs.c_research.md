# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose

`rpc_pipefs.c` implements the pNFS blocklayout pipefs upcall used to resolve simple block volume signatures into Linux device major/minor numbers. It also registers the per-network-namespace `blocklayout` rpc_pipefs node used by the userspace helper.

## Main Responsibilities

- Encode a simple block volume into the blocklayout daemon message format.
- Queue an upcall to userspace via rpc_pipefs and wait for a downcall response.
- Decode the daemon's `bl_dev_msg` response into a `dev_t`.
- Provide pipe downcall and destroy callbacks.
- Create and remove `/.../nfs/blocklayout` pipefs dentries on rpc_pipefs mount/umount events.
- Manage per-net initialization and cleanup of blocklayout pipe state.

## Key Functions

- `bl_resolve_deviceid()` serializes a simple volume, queues `BL_DEVICE_MOUNT`, sleeps on `nn->bl_wq`, and returns `MKDEV(reply->major, reply->minor)` when userspace reports `BL_DEVICE_REQUEST_PROC`.
- `nfs4_encode_simple()` emits a single simple-volume XDR-like payload including signature offsets and opaque signature bytes.
- `bl_pipe_downcall()` validates response length, copies `struct bl_dev_msg` from userspace into `nn->bl_mount_reply`, and wakes the waiter.
- `bl_pipe_destroy_msg()` wakes the waiter if the queued upcall was destroyed with an error.
- `rpc_pipefs_event()` reacts to `RPC_PIPEFS_MOUNT` and `RPC_PIPEFS_UMOUNT`.
- `bl_init_pipefs()` and `bl_cleanup_pipefs()` register/unregister the notifier and pernet subsystem.

## Control Flow and State

`bl_resolve_deviceid()` serializes all blocklayout upcalls per network namespace with `nn->bl_mutex`. It temporarily increments `b->simple.len` to account for the single-volume wrapper, allocates an upcall buffer, queues it with `rpc_queue_upcall()`, sets the task state to uninterruptible, and waits for a downcall/destroy wakeup. The response is stored in the per-net `nn->bl_mount_reply`.

Per-net state consists of `bl_mutex`, `bl_wq`, and `bl_device_pipe`. The pipe is created with `rpc_mkpipe_data()` and registered into mounted pipefs superblocks when available.

## Integration Points

- Called from `dev.c` by `bl_parse_simple()`.
- Uses `struct nfs_net` fields for shared NFS per-net state.
- Uses SUNRPC pipefs helpers `rpc_mkpipe_data()`, `rpc_mkpipe_dentry()`, `rpc_queue_upcall()`, `rpc_unlink()`, and notifier registration.
- Exposes the blocklayout device resolver to a userspace daemon that knows how to map simple signatures to block devices.

## Risks and Edge Cases

- The wait is uninterruptible and has no local timeout; progress depends on userspace or message destruction.
- `b->simple.len` is incremented in place for the wrapper before message size validation, so callers should not reuse the same decoded volume assuming the original length.
- Only one outstanding simple-volume upcall per net namespace is allowed by the mutex and single reply slot.
- If rpc_pipefs is not mounted, per-net registration returns success without creating a visible pipe until a later mount event.

## Testing Focus

Important cases include absent pipefs mounts, userspace returning non-success status, malformed downcall lengths, upcall queue failure, message destruction wakeup, and concurrent simple-volume resolutions within one network namespace.
