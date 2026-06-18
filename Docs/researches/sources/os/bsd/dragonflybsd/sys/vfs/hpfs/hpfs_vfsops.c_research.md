# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_vfsops.c

Source read: complete file, 569 lines.

Purpose: HPFS VFS operation implementation. It handles mount/update, device opening, super/spare block validation, bitmap/codepage initialization, root lookup, unmount cleanup, statfs, NFS file handles, vnode instantiation, export checks, and VFS registration.

Key interfaces:
- `hpfs_mount()` copies `hpfs_args`, handles export-only updates, resolves the block device with namecache lookup, verifies disk vnode type, records mount-from name, and calls `hpfs_mountfs()`.
- `hpfs_mountfs()` prevents duplicate/in-use mounts, invalidates old buffers, opens the device read-only or read-write, reads super/spare blocks, validates magic numbers, initializes `hpfsmount`, bitmap and codepage state, installs vnode ops, resolves root, and records fsid/local flags.
- `hpfs_unmount()` flushes vnodes, closes the device, invalidates buffers, frees codepage and bitmap memory, clears mount data, and frees `hpfsmount`.
- `hpfs_root()`, `hpfs_statfs()`, `hpfs_fhtovp()`, `hpfs_vptofh()`, and `hpfs_checkexp()` implement standard VFS services.
- `hpfs_vget()` creates or finds vnodes, reads fnode sectors, validates `FN_MAGIC`, initializes `hpfsnode`, inserts into the hash, and sets vnode type.

Integration:
- Registers `hpfs_vfsops` with `VFS_SET(hpfs_vfsops, hpfs, 0)` and `MODULE_VERSION(hpfs, 1)`.
- Uses `hpfs_hphashinit()` during VFS init and `hpfs_hphash_uninit()` during VFS uninit.
- Adds `hpfs_vnode_vops` to the mount's normal vnode ops.

Risks and review notes:
- `hpfs_vget()` sets `hp->h_gid = hpmp->hpm_uid`; this looks like a uid/gid mix-up and can make all nodes report the uid as gid.
- Several failure paths after partial mount initialization require careful cleanup ordering; `mp->mnt_data` and `dev->si_mountpoint` are cleared in the common failure path.
- HPFS file handles do not validate generation numbers because create/unlink are not supported.
