# File Research: sources/os/linux/linux/fs/fuse/fuse_i.h

Purpose: Central internal FUSE header defining connection, inode, file, request, queue, mount, IO, DAX, passthrough, and helper interfaces used across the Linux FUSE implementation.

Key responsibilities:
- Defines constants for max pages, name limits, request timeout frequency, control dentries, and writeback exclusion bias.
- Defines `struct fuse_inode`, including nodeid/nlookup/FORGET state, attribute cache state, writeback state, readdir cache state, DAX/passthrough state, and submount lookup tracking.
- Defines inode state bits for readdirplus advice, bad inode state, btime cache, cache IO mode, size instability, and exclusive access.
- Defines `struct fuse_file`, including FUSE handle, kernel handle, open flags, readdir state, poll rbtree node, IO mode, passthrough file, and flock state.
- Defines request argument containers: `fuse_in_arg`, `fuse_arg`, `fuse_args`, `fuse_args_pages`, `fuse_io_args`, and release/open union storage.
- Defines async IO state in `struct fuse_io_priv`.
- Defines request flags and `struct fuse_req`, including headers, waitqueue, mount pointer, arg buffer, io_uring fields, and creation timestamp.
- Defines input and processing queues: `fuse_iqueue`, `fuse_iqueue_ops`, `fuse_pqueue`, and `fuse_dev`.
- Defines `struct fuse_conn`, the main negotiated connection state and capability bitmap, with background request accounting, mount list, device list, timeout state, DAX/passthrough/io_uring pointers, and sync bucket.
- Defines `struct fuse_mount`, allowing multiple superblocks/submounts to share one `fuse_conn`.
- Provides inline helpers for mount/connection/inode lookup, nodeid access, stale checks, bad inode marking, folio descriptor allocation, sync bucket decrement, and passthrough access.
- Declares cross-file APIs for lookup, forget, device lifecycle, request submission, inode operations, file IO, xattrs/ACLs, DAX, passthrough, ioctl, readdir, mount lifecycle, invalidation, and sysctl.

Important data/control flow:
- `fuse_conn` is the negotiated protocol and lifecycle anchor; `fuse_mount` maps it to each superblock.
- `fuse_inode` keeps kernel inode state aligned with userspace node identity and attribute invalidation.
- `fuse_file` holds per-open server file handle and kernel handle used by poll notifications.
- `fuse_args` is the uniform request descriptor used by all opcode implementations.
- Connection feature bits are set in `inode.c` after `FUSE_INIT` and consumed in `dir.c`, `file.c`, xattr, DAX, passthrough, and device code.

External dependencies:
- Linux VFS, folio/page-cache, waitqueue, workqueue, pid/user namespace, xattr, idr, DAX, io_uring, and FUSE UAPI headers.
- Companion implementation files in `fs/fuse`.

Notable edge cases:
- Many `no_*` fields are negative capability caches set after `-ENOSYS`.
- `FUSE_I_SIZE_UNSTABLE` blocks stale attribute application during truncate/extend races.
- `FUSE_NOWRITE` is a negative counter bias, not a boolean.
- Passthrough and DAX fields compile conditionally and have NULL inline fallbacks.
