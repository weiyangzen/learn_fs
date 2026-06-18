# File Research: sources/os/linux/linux/fs/afs/inode.c

## Purpose
Manages AFS vnode/inode initialization, status application, callback commitment, inode lookup, root inode creation, attributes, eviction, and setattr.

## Main Responsibilities
- Converts AFS file status records into Linux inode mode, ownership, size, ops, mapping ops, and cache state.
- Applies returned vnode status and callback promises after fileserver operations.
- Detects data-version jumps and invalidates cached directory/file data when needed.
- Creates and looks up inodes by AFS fid.
- Handles getattr, drop-inode policy, eviction cleanup, and setattr operations.

## Key Functions and Data
- `afs_inode_init_from_status()` initializes new inodes from server status and assigns file, dir, symlink, or mountpoint operations.
- `afs_apply_status()` updates existing inodes, handles data-version changes, size changes, directory invalidation, and page-cache sizing.
- `afs_vnode_commit_status()` applies status/callback results or deletion/unlink outcomes under `vnode->cb_lock`.
- `afs_fetch_status()` performs a one-vnode fetch-status operation.
- `afs_iget()` and `afs_root_iget()` create regular and root inodes from fids/status.
- `afs_getattr()` validates stale callback state unless `AT_STATX_DONT_SYNC` is used.
- `afs_evict_inode()` flushes directory/symlink data, waits for netfs I/O, clears fscache/writeback/key/permit state.
- `afs_setattr()` coordinates size and metadata changes through AFS/YFS setattr RPCs and netfs/fscache resizing.

## Important Details
- Symlinks with mode `0644` are treated as AFS mountpoints and exposed as automount directories.
- Directories are marked single-no-upload and assumed locally valid after initialization.
- Data-version mismatch can mark files for data zap or invalidate directory contents.
- `afs_get_inode_cache()` builds an fscache key from vnode id, unique, and extended vnode id fields for YFS-compatible 96-bit vnode IDs.
- Pseudodir inodes use immediate drop semantics in `afs_drop_inode()`.
