# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_inode.h

Purpose: Defines the in-memory CHFS inode structure and compatibility constants/macros used by the vnode and UFS-derived code paths.

Key definitions:
- `CHFS_ROOTINO` is inode 2.
- `enum chtype`: CHFS file types, intentionally aligned for conversion with NetBSD `enum vtype`.
- `CHTTOVT`, `VTTOCHT`, `IFTOCHT`: conversions between CHFS type, vnode type, and mode bits.
- `struct chfs_inode`: CHFS inode embedding `genfs_node`, locks, mount pointers, vnode pointer, vnode-cache pointer, dirent list, fragment tree, metadata fields, flags, device number, and symlink target.
- `VTOI`, `ITOV`: vnode/inode conversions.
- UFS permission and file-type constants copied locally for compatibility.

Important fields:
- `chvc`: the inode’s `struct chfs_vnode_cache`.
- `dents`: in-memory directory entry list.
- `fragtree`: red-black tree of file fragments.
- `version`, `size`, `write_size`: append-log versioning and file length tracking.
- `iflag`: pending timestamp/update flags.

Dependencies:
- Kernel-only includes vnode, stat, UFS mount, and genfs node APIs.
- Used throughout mount, vnode, read-inode, write, and GC code.

Research notes:
- Comments note some UFS dependencies and duplicated constants should eventually be removed.
- `ctime` is described as creation time in the struct comment, but used as change time semantics in CHFS update paths.
