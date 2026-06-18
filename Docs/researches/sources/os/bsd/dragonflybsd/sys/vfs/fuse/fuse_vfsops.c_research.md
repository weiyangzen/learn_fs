# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vfsops.c

Implements FUSE filesystem VFS operations and module lifecycle. It registers `fuse_vfsops` with `VFS_SET(fuse_vfsops, fuse, VFCF_SYNTHETIC | VFCF_MPSAFE)` and exposes sysctls for ABI version and debug logging.

`fuse_cmp_version` compares negotiated userspace ABI version with a requested version. `fuse_mount_kill` atomically marks a mount dead, wakes sleepers, and sends kqueue notifications. `fuse_mount_free` releases a mount refcount and frees locks, credentials, and memory when the final reference drops.

`fuse_mount` rejects update mounts, copies `struct fuse_mount_info`, fills mount source and mountpoint strings, optionally appends a subtype to `f_fstypename`, resolves and access-checks the `/dev/fuse` path, checks `SYSCAP_NOMOUNT_FUSE`, retrieves the open device file by fd, and obtains its devfs private `struct fuse_mount`.

Mount initialization sets locks, queues, RB tree, device vnode, credentials, mount flags, and root node. It installs FUSE normal/spec vnode ops, sends `FUSE_INIT` to userspace, records negotiated major/minor/max_write, rejects protocol versions older than 7.0, runs initial `VFS_STATFS`, initializes the helper bio queue/spinlock, and starts `fuse_io_thread`.

`fuse_unmount` locks the mount, flushes vnodes, sends `FUSE_DESTROY` if the mount is not already dead, kills the mount, waits for the helper thread to exit, frees the root node, closes/releases the device vnode, drops mount data/local flag, and releases the mount reference.

`fuse_sync` scans mount vnodes for dirty buffer trees and calls `VOP_FSYNC`. It uses a two-stage scan: a fast pre-check (`fuse_sync_scan1`) skips clean vnodes, then `fuse_sync_scan2` performs the flush.

`fuse_root` returns the root vnode from `fmp->rfnp`, marks it `VROOT`, and asserts directory type.

`fuse_statfs` and `fuse_statvfs` send `FUSE_STATFS`, copy `struct fuse_kstatfs` values into DragonFly `statfs`/`statvfs`, and set I/O sizes using `FUSE_BLKSIZE`.

`fuse_init` initializes node and IPC caches and creates `/dev/fuse`; on device creation failure it unwinds caches. `fuse_uninit` destroys IPC cache, node cache, and the character device.

Important dependencies: `/dev/fuse` state from `fuse_device.c`, IPC from `fuse_ipc.c`, node management from `fuse_node.c`, ABI definitions from `fuse_abi.h`, and vnode ops/helper I/O from files outside this group.

Notable risks or research hooks: mount error paths after partial initialization sometimes return after `vrele(devvp)` but before fully undoing mount state; worth auditing with the full `fuse_vnops.c` and helper thread implementation. Mount flags from `fuse_mount_info` are mostly parsed but not broadly enforced here.
