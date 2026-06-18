# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/inode.h

Kernel UFS inode wrapper header. It defines the in-core inode structure that pairs DragonFly vnode state with an on-disk UFS1 dinode and filesystem-specific transient fields.

Key responsibilities:
- Defines `ufs_lbn_t` as the logical block number type and `doff_t` for directory offsets.
- Defines `struct inode` under kernel/kernel-structure builds, including hash linkage, vnode/device references, flags, device and inode number identity, effective link count, filesystem pointer, quota pointers, NFS modification revision, byte-range lock state, directory lookup side-effect fields, directory hash pointer, and embedded `struct ufs1_dinode`.
- Provides field aliases from `i_din` to convenient inode names such as `i_size`, `i_mode`, `i_nlink`, direct/indirect block arrays, uid/gid, timestamps, generation, and block count.
- Defines inode flags for access/change/update/modified state, rename, shared/exclusive lock markers, hash membership, lazy modification, and special no-copy-write behavior.
- Defines `struct indir` for logical block path calculations used by truncate and bmap code.
- Defines `VTOI()` and `ITOV()` conversion macros.
- Defines `DOINGSOFTDEP()` and `DOINGASYNC()` mount-flag checks.
- Defines `struct ufid`, the UFS file-handle payload used for NFS/exported file handle conversion.

Dependencies:
- Includes `dinode.h` and queue definitions; kernel builds include lock and lockf headers.
- References `struct fs`, `struct vnode`, `cdev_t`, quota structures, and directory hash state.

Notable risks:
- `struct inode` is central in-core filesystem state; alias macros mean changes to `ufs1_dinode` fields directly affect most UFS code.
- `i_effnlink` is important for softdep delayed link-count semantics and must be kept consistent with `i_nlink` and `inodedep` state.
- Comments note `i_spare` is not truly spare for ext2fs, so shared ancestry with other filesystems constrains changes.
