# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/namefs/namevfs.c

## Role

Implements the VFS side of NAMEFS, the filesystem behind descriptor-to-path attachment such as `fattach()`. It mounts an open file descriptor onto a filesystem node and presents the descriptor’s vnode through a synthetic namefs vnode.

## Major Responsibilities

- Registers NAMEFS VFS and vnode operations.
- Allocates unique namenode inode numbers.
- Maintains a global hash from mounted file vnode to `struct namenode`.
- Supports walking all namefs mounts for a file vnode.
- Forces unmounts of all namefs mounts for a vnode, used for stream/pipe close cases.
- Implements mount, unmount, root, statvfs, sync, and syncfs.
- Maintains stream `STRMOUNT` state while streams are attached.

## Key Functions

- `namenodeno_alloc()`, `namenodeno_init()`, `namenodeno_free()`: Allocate/free unique node IDs from a vmem arena, extending the arena in `NM_INOQUANT` chunks.
- `nameinsert()`: Adds a namenode to `nm_filevp_hash`.
- `nameremove()`: Removes a namenode from the hash.
- `namefind()`: Finds a namenode by mounted file vnode and optionally mountpoint vnode.
- `nm_walk_mounts()`: Calls a callback for every namenode mounted from a given file vnode.
- `nm_umountall()` / `nm_unmountall()`: Force-unmount every namefs mount associated with a vnode, retrying on `EBUSY`.
- `nm_mount()`: Main file-descriptor mount implementation.
- `nm_unmount()`: Removes the namenode, drops the root reference, frees or de-roots the synthetic vnode, clears stream mount state if this was the last mount, and closes the held file.
- `nm_root()`: Holds and returns the mounted descriptor root vnode.
- `nm_statvfs()`: Returns simple synthetic statvfs data.
- `nm_sync()`: On `SYNC_CLOSE`, force-unmounts all mounts for the file vnode; otherwise fsyncs the mounted file vnode.
- `nm_syncfs()`: Directed syncfs, accepting only zero flags, fsyncs the mounted file vnode.
- `nameinit()`: Registers VFS ops, dummy VFS ops, vnode ops, initializes device number, hash table, locks, and the dummy `namevfs`.
- `_init()`, `_fini()`, `_info()`: Module lifecycle; `_fini()` returns `EBUSY`.

## Mount Semantics

`nm_mount()` performs:

- Validates `struct namefd` size and copies it from user space.
- Resolves the file descriptor to a `struct file` and vnode.
- Rejects busy/namefs mountpoints and roots.
- Rejects attaching inside `/dev/pts` or `/dev/vt` via specfs realvp checks.
- Rejects directory and event port file descriptors.
- Requires mount privilege if the descriptor is neither a door nor a stream.
- Rejects descriptors that are themselves filesystem roots.
- Reads attributes from both mountpoint and descriptor vnode.
- Requires caller ownership or privilege over the mountpoint.
- Requires write access on the mountpoint.
- Rejects descriptor vnodes with file/record locks.
- Sets `STRMOUNT` on streams.
- Holds the file structure and stores it in the namenode.
- Builds synthetic vnode attributes: descriptor type/size/rdev/block info, synthetic fsid/nodeid, one link.
- Allocates and initializes the namefs root vnode.
- Marks VFS as `VFS_UNLINKABLE`, assigns synthetic fsid/dev/data, and sets a generated resource string like `unspecified_<fstype>_<nodetype>`.
- Inserts the namenode into the global hash table.

## Data Structures and Globals

- `namedev`: Synthetic device number for namefs.
- `namefstype`: Registered filesystem type.
- `nm_filevp_hash[]`: Hash table keyed by `nm_filevp`.
- `namevfs`: Dummy VFS used for temporary namefs nodes.
- `ntable_lock`: Global hash lock.
- `nm_inoarena` and `nm_inolock`: Unique inode allocator state.
- `struct namenode`: Holds mounted file vnode/file pointer, mountpoint vnode, synthetic vnode, attributes, flags, and hash linkage.

## Unmount and Lifetime Semantics

`nm_unmount()`:

- Rejects forced unmount with `ENOTSUP`.
- Requires owner/privilege according to stored mountpoint uid.
- Removes the namenode from the global hash.
- Drops the mounted root vnode count under vnode lock.
- If count reaches zero, invalidates/frees vnode, releases VFS, frees node ID and namenode, and later closes the held file.
- If still referenced, clears `VROOT` so inactive cleanup can finish later.
- Clears stream `STRMOUNT` only when no more namefs mounts reference the same file vnode.

`nm_unmountall()` loops until `nm_umountall()` stops returning `EBUSY`, yielding briefly between attempts.

## Edge Cases and Semantics

- Multiple mountpoints may attach the same file descriptor vnode; hash entries are unique per mountpoint.
- `nm_walk_mounts()` supports callers that need to act on every namefs attachment for a vnode.
- There is a race window in forced unmount-all because `ntable_lock` must be dropped around `dounmount()`. The code documents that new mounts may appear during the window.
- NAMEFS does not support forced unmount for normal unmount.
- `nm_sync()` with `SYNC_CLOSE` is a cleanup trigger for all mounts of the underlying vnode.
- The mounted descriptor’s own VFS is used to derive the generated resource string, but failure falls back to a generic nodetype resource.

## Dependencies

Pairs with NAMEFS vnode operations from `nm_vnodeops_template` in another source file. Uses file descriptor APIs (`getf`, `releasef`, `closef`), vnode/VFS allocation and registration, stream locks, specfs/devpts/devvt checks, privilege policy, vmem, statvfs, and generic mount/unmount infrastructure.
