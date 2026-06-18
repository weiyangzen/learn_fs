# File Research: sources/os/linux/linux/fs/orangefs/orangefs-kernel.h

Central private OrangeFS kernel header defining structures, globals, helpers, and cross-file prototypes.

Key contents:
- Constants for default op/slot timeouts, device name, protocol magic, purge retry count, and max up/down device request sizes.
- `orangefs_vfs_op_states` and helpers/macros for waiting, in-progress, serviced, purged, given-up, and cancel states.
- `orangefs_kernel_op_s`, the queued RPC object containing tag, shared-memory slot state, upcall/downcall payloads, completion, lock, attempts, and list node.
- `orangefs_inode_s`, per-inode private state containing OrangeFS object ref, symlink target, xattr semaphore/cache, VFS inode, getattr/mapping timeouts, pending attr credentials, and bitlock.
- `orangefs_sb_info_s`, per-superblock private state containing root handle, fsid, mount id, mount flags, device name, pending state, and list linkage.
- Stats, cached xattr, and write-range structures.
- `ORANGEFS_I()` and `ORANGEFS_SB()` accessors.
- Khandle-to-inode hash conversion, root-handle check, and handle matching helpers.
- Prototypes for op cache, inode cache, module purge, waitqueue purge, superblock, inode, device, file, utility, xattr, and service-operation APIs.
- Operation flags for interruptible, priority, cancellation, no-mutex, async, and writeback operation modes.
- `fill_default_sys_attrs()` for create/mkdir/symlink requests and `orangefs_set_timeout()` for dentry expiration.

Important role:
- This header defines the local contract between OrangeFS VFS glue, request scheduling, userspace bridge, inode/page-cache code, and sysfs/debugfs controls.
