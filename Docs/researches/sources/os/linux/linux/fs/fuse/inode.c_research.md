# File Research: sources/os/linux/linux/fs/fuse/inode.c

Purpose: Implements FUSE inode allocation/lifecycle, attribute reconciliation, superblock/mount setup, mount option parsing, INIT negotiation, connection/device lifecycle integration, export support, syncfs/statfs, submounts, and module initialization/cleanup.

Key responsibilities:
- Defines module metadata and global state: inode slab cache, global connection list, `fuse_mutex`, `/dev/fuse` waitqueue, page/request limits, and background request limits.
- Allocates and frees `struct fuse_inode`, including FORGET request storage, DAX inode data, passthrough backing refs, locks, and invalidation state.
- Evicts inodes by truncating pages, sending FORGET for outstanding lookups, cleaning DAX/submount state, and bumping evict counter for non-deleted inodes.
- Applies FUSE attributes to inodes through `fuse_change_attributes_common()` and `fuse_change_attributes_i()`, respecting writeback-cache local size/mtime/ctime.
- Creates and looks up inodes with `fuse_iget()`, including stale inode detection, reused nodeid handling, and special un-hashed submount mountpoint inodes.
- Implements reverse invalidation for inode page/attribute cache and dentry entries.
- Implements `statfs`, `sync_fs`, writeback sync buckets, and superblock operations.
- Parses mount options: source, fd, rootmode, user/group IDs, default permissions, allow_other, max_read, blksize, and subtype.
- Initializes `fuse_conn`, request queues, background limits, pid/user namespaces, poll tree, attr/evict versions, max pages, and passthrough backing maps.
- Negotiates server capabilities in `process_init_reply()` after `FUSE_INIT`, setting feature bits for async read/DIO, locks, export, writeback cache, readdirplus, ACLs, DAX, passthrough, idmapped mounts, request timeout, io_uring, and more.
- Builds `FUSE_INIT` requests in `fuse_new_init()` and supports sync or background init.
- Allocates/installs/releases `struct fuse_dev` instances and their processing queues.
- Fills superblocks for normal FUSE, fuseblk, and submounts, including BDI setup, root inode creation, dentry operations, control filesystem registration, and device install.
- Implements NFS export file-handle encoding/lookup when export support is negotiated.
- Registers/unregisters `fuse` and `fuseblk` filesystem types, sysctl, `/dev/fuse`, sysfs mount point, fusectl, and dentry invalidation infrastructure.

Important data/control flow:
- `fuse_fill_super_common()` wires the mount context, connection, superblock, root inode, BDI, control fs entry, and optional device fd together.
- `fuse_send_init()` gates connection readiness; `process_init_reply()` sets `fc->conn_init` or `fc->conn_error`, then wakes blocked waiters.
- `fc->killsb` protects traversal of all mounts sharing a connection.
- `fc->curr_bucket` and `struct fuse_sync_bucket` allow `syncfs()` to wait for already-issued writeback without racing newer writes.
- Mount teardown removes the mount from `fc->mounts`; the last mount sends DESTROY if requested, aborts the connection, removes fusectl state, and drops the connection.

External dependencies:
- Core declarations in `fuse_i.h`, device declarations in `fuse_dev_i.h`, and io_uring declarations in `dev_uring_i.h`.
- Linux VFS fs_context, superblock, exportfs, BDI, DAX, namespace, module, sysfs, and block-device APIs.
- Other FUSE implementation files for device, control fs, DAX, passthrough, sysctl, request abort, and timeout behavior.

Notable edge cases:
- Mount fd must be a FUSE device opened in the same user namespace as the mount context.
- Reconfigure rejects changes except legacy remount option compatibility.
- `FUSE_ALLOW_IDMAP` is accepted only when `default_permissions` is active.
- Passthrough is rejected with writeback cache and invalid stack depth.
- For submounts, root inode state is duplicated from the mountpoint and lookup reference ownership is shared through `fuse_submount_lookup`.
