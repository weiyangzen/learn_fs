# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vfsops.c

Tmpfs VFS operation implementation for mount/remount, unmount, root lookup, NFS file handles, statfs, sync, module init/uninit, and DDB diagnostics.

Key responsibilities:
- Defines tmpfs mount option names for size, max file size, inode count, uid/gid/mode, extended attribute memory, namecache policy, mmap mtime policy, symlink following, page-cache read mode, and union/export options.
- Implements lazy and full mmap mtime update scans over mount vnodes.
- Scans all process VM maps to find tmpfs writable mappings for a mount and optionally revoke write protections by clearing `VM_PROT_WRITE` and calling `pmap_protect()`.
- Converts a read-write tmpfs mount to read-only by suspending writes, checking writable mappings, setting mount/tmpfs read-only state, revoking writable mappings in forced mode, updating mtimes, and flushing vnodes.
- Handles remounts by rejecting changes to fixed parameters such as uid/gid/mode, inode limit, size, max file size, nonc, and pgread, while allowing `easize`, `nomtime`, and RO/RW transitions.
- Computes default mount size, page limit, and inode limit from available memory/swap, explicit options, and per-page node density.
- Initializes `struct tmpfs_mount`, inode allocator, root node, mount flags, fast-lookup flags, filesystem id, mount-from string, and name length.
- Unmounts by suspending writes, flushing vnodes until empty or returning `EBUSY`, destroying remaining directory contents/nodes under the all-node lock, clearing `mnt_data`, freeing mount state, and resuming writes.
- Frees mount structures only when the mount refcount drops to zero; VM objects may outlive unmount, so page-used count is not asserted at final mount free.
- Implements cached root lookup through `tmpfs_alloc_vp()`.
- Implements NFS file-handle to vnode conversion by matching inode and generation in the used-node list and taking a transient node reference.
- Reports statfs blocks from page limits/current memory availability and files from node limits/current node count.
- Implements sync handling for suspend state and lazy mtime updates.
- Initializes tmpfs support via `tmpfs_subr_init()` and installs tmpfs file close operation wrapper into `tmpfs_fnops`; uninitializes through `tmpfs_subr_uninit()`.
- Registers tmpfs as a jail-allowed VFS with root/statfs/fhtovp/sync/init/uninit operations.
- Provides DDB `show tmpfs` output for mount memory, inode, extended attribute, refcount, size, read-only, namecache, and mtime policy state.

Dependencies:
- FreeBSD VFS mount/update/unmount, vnode traversal, write suspension, allproc/proc/vmspace locking, VM map entries, pmap protection, jail/VFS flags, DDB, and tmpfs support APIs.
- Tmpfs root/node allocation, vnode allocation, directory destruction, memory accounting, and file operation wrappers from `tmpfs_subr.c`.

Notable risks:
- RW-to-RO remount touches process address spaces system-wide; races are controlled through process/vmspace references and VM map locks.
- Forced RO conversion can revoke write permissions from existing mappings, which may surprise mapped writers but is required to complete the transition.
- Unmount must coordinate VFS write suspension with node destruction so no concurrent creator can attach new nodes.
- File-handle lookup is linear over used nodes and returns `EINVAL` for stale/missing handles rather than `ESTALE`.
- `tmpfs_free_tmp()` allows lingering VM objects after unmount, so mount lifetime is tied to regular-file object references.
