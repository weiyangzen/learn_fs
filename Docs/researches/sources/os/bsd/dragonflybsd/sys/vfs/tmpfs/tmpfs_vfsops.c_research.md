# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_vfsops.c

This file implements TMPFS VFS operations: mount, unmount, root lookup, file-handle conversion, export checks, and statfs.

Mount parses optional `tmpfs_mount_info`, applies root defaults and non-root restrictions, computes page/node/file-size limits from requested size, swap size, and physical memory, allocates the mount structure and per-mount malloc zones, creates the root directory node, marks root `SF_NOCACHE`, initializes mount flags, installs normal and FIFO vnode ops, fills mount stat names, and populates initial statfs data.

Unmount takes the mount token, optionally enables forced close, truncates regular-file nodes before vnode flushing so data can be discarded, calls `vflush`, removes all directory entries, drops the root link, frees every remaining node, destroys per-mount allocation zones, checks page/node counters, and frees the mount structure.

`tmpfs_root` returns a vnode for the root node through `tmpfs_alloc_vp`. `tmpfs_fhtovp` scans used nodes for a matching inode/generation file handle and returns a vnode. `tmpfs_vptofh` writes the tmpfs file handle. `tmpfs_checkexp` integrates with DragonFly export lookup.

`tmpfs_statfs` reports page-sized blocks, free/used page counts, free node counts, and root owner. The file registers TMPFS as `VFCF_MPSAFE`.
