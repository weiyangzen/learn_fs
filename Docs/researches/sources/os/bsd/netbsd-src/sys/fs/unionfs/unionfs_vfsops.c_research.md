# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vfsops.c

Read completely: 569 lines.

Implements VFS operations and module registration for the newer `unionfs` layer. `unionfs_mount()` rejects root and update mounts, supports `MNT_GETARGS`, derives default uid/gid/mode from the covered vnode, resolves the target path with `namei()`, supports `UNMNT_ABOVE` and `UNMNT_BELOW` but rejects `UNMNT_REPLACE`, initializes copy mode as transparent and whiteout mode as always, checks whiteout support for writable mounts, creates the root unionfs vnode, sets MPSAFE/local/readonly flags, assigns a new fsid, and fills `f_mntfromname` with `<above>:` or `<below>:` prefixes.

`unionfs_unmount()` repeatedly calls `vflush()` to drain vnodes, optionally force-closing, then frees the mount structure. `unionfs_root()` returns the cached root vnode. `unionfs_quotactl()` delegates to the upper mount, `unionfs_statvfs()` combines lower and upper filesystem statistics, `unionfs_sync()` is a no-op, and rename locks delegate to the upper filesystem. The table wires standard VFS hooks but leaves vget, file handles, snapshots, suspend, and fsync unsupported.

Module init attaches the VFS and creates a `CTL_VFS` sysctl node named `union`; module fini detaches and tears down the sysctl log.

Risks and notes: the MPSAFE check appears to test `upperrootvp->v_mount->mnt_flag & IMNT_MPSAFE` instead of `mnt_iflag`; `unionfs_unmount()` frees only `unionfs_mount` and relies on vnode reclamation for root/layer references; update mounts are unsupported; `UNMNT_REPLACE` is rejected despite being defined in the shared mount flags; the sysctl VFS number 15 is hard-coded.
