# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs.h

This is the main TMPFS internal header. It defines directory entries, directory RB trees, node structures, mount structures, file handles, locking macros, conversion helpers, and support-function prototypes.

Directories are represented by `struct tmpfs_dirent` entries stored in two RB trees: one ordered by name and one ordered by cookie. TMPFS does not store physical `.` or `..` entries; readdir synthesizes them. Cookies are derived from dirent addresses and masked to positive 64-bit offsets.

`struct tmpfs_node` holds common vnode attributes, timestamps, flags, link count, vnode association, interlock, vnode state, and type-specific data. Type-specific storage includes device IDs, directory parent/tree state, symlink target, regular-file backing VM object/accounting, and FIFO hooks.

`struct tmpfs_mount` stores mount limits and counters: max pages, used pages, root node, max/in-use nodes, max file size, used-node list, per-mount malloc zones, inode counter, export data, and mount references. The mount token macros use the DragonFly mount token.

The header exposes allocation, directory, vnode, resize, attribute, timestamp, truncate, and rename-lock ordering helpers implemented by `tmpfs_subr.c` and used by vnode/VFS ops.
