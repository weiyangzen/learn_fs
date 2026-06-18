# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_dir.c

Read completely: 175 lines.

Purpose: tracks referenced devfs directory paths to prevent device creation path conflicts and to prune directory references when user symlinks or entries are removed.

Key structures:
- `struct dirlistent` stores a directory string, refcount, and list link.
- `devfs_dirlist` is protected by `dirlist_mtx`.

Key functions:
- `devfs_dir_find()` returns true if any tracked directory path contains the queried path.
- `devfs_dir_findent_locked()` finds an exact tracked path under lock.
- `devfs_dir_ref()` inserts or increments a directory reference, ignoring empty paths.
- `devfs_dir_ref_de()` derives a fully qualified devfs path from a dirent and references it.
- `devfs_dir_unref()` decrements and removes/free entries at refcount zero.
- `devfs_dir_unref_de()` dereferences by dirent-derived path.
- `devfs_pathpath()` returns true if path `p1` contains path `p2`, treating exact match or directory prefix as containment.

Research notes:
- The directory list is separate from the per-mount dirent tree.
- It is used by device creation/path conflict checks in `devfs_devs.c`.
