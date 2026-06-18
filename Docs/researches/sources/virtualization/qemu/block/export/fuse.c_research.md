# File Research: sources/virtualization/qemu/block/export/fuse.c

Implements the FUSE block export driver, presenting a block node as a single raw regular file mounted at a chosen path. It uses FUSE protocol 7.x low-level device handling directly, while libfuse is used for session setup/mount/unmount.

`FuseExport` extends `BlockExport` with a FUSE session, in-flight counter, mount/handler/halted state, one or more `FuseQueue`s, mountpoint, writable/growable/allow-other flags, and atomic stat metadata. Each queue has an AioContext, FUSE FD, and cached aligned write-data buffer. Multi-iothread export creates one queue per supplied AioContext and clones `/dev/fuse` FDs with `FUSE_DEV_IOC_CLONE`; otherwise a single queue follows the block backend's AioContext.

Creation checks mountpoint uniqueness, verifies the mountpoint is a regular file, sets permissions and ownership defaults, optionally tries `allow_other` automatically, mounts with `rw/ro,nosuid,nodev,noatime,max_read,default_permissions`, makes the FUSE FD nonblocking, clones extra queue FDs, installs fd handlers, and configures block dev ops for draining. Draining detaches handlers, waits for atomic in-flight requests, refreshes AioContext on end, and reattaches handlers unless halted.

Request intake uses `readv()` so FUSE WRITE payloads land directly in an aligned data buffer. It validates header size, request length, supported opcode header lengths, old/new `fuse_init_in` layout differences, truncated requests, and writes immediate `-ENOSYS`/`-EINVAL` errors where needed. Requests run in coroutines with a graph read lock.

Supported operations include INIT, STATFS, OPEN, GETATTR, SETATTR, READ, WRITE, FALLOCATE, FSYNC, FLUSH, optional LSEEK, DESTROY/RELEASE no-ops, and LOOKUP returning `ENOENT` for anything besides the root. Reads short-read at EOF and allocate aligned response buffers. Writes enforce writability, handle fixed-size short writes or growable truncation, guard offset overflow, and use `blk_co_pwrite()`. Fallocate supports EOF preallocation, optional punch-hole, and optional zero-range by truncating/zero-writing in chunks. LSEEK maps `SEEK_DATA`/`SEEK_HOLE` through block status and handles EOF visibility.

Responses are written either as a single `FuseRequestOutHeader` or header-plus-buffer for read data. Shutdown detaches handlers and removes the mountpoint from the global export table; delete closes cloned FDs, frees cached buffers/queues, unmounts/destroys the session, and frees the mountpoint. The exported driver is `blk_exp_fuse`.
