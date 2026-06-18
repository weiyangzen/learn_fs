# File Research: sources/os/linux/linux-stable/fs/debugfs/inode.c

## Purpose

`inode.c` implements the debugfs pseudo-filesystem: mount context parsing, superblock/inode setup, public create APIs, recursive removal, rename support, enable/disable boot handling, and filesystem registration.

## Main Responsibilities

- Registers the `debugfs` filesystem and `/sys/kernel/debug` mount point.
- Parses mount options `uid`, `gid`, `mode`, and `source`.
- Applies root inode ownership/mode options on mount and remount.
- Allocates debugfs-specific inodes from `debugfs_inode_cache`.
- Creates files, directories, automounts, and symlinks.
- Removes debugfs trees while coordinating with active file users.
- Supports lookup, lookup-and-remove, and `debugfs_change_name()`.
- Tracks whether debugfs is enabled and registered.

## Core Data Flow

Mount setup:
- `debugfs_init_fs_context()` allocates `struct debugfs_fs_info` and installs fs-context operations.
- `debugfs_get_tree()` uses `get_tree_single()` with `debugfs_fill_super()`.
- `debugfs_fill_super()` calls `simple_fill_super()`, sets super operations, installs dentry operations, marks dentries `DCACHE_DONTCACHE`, and applies mount options.

Creation:
- `debugfs_start_creating()` checks enable/registration state, pins the filesystem, chooses the root if parent is NULL, and starts simple creation.
- `__debugfs_create_file()` creates a regular inode, stores `i_private`, real fops/short fops/raw pointer, aux data, and uses `d_make_persistent()`.
- Directory and automount creators set directory inode operations, link counts, and fsnotify events.
- Symlink creation duplicates target text into `i_link`.

Removal:
- `debugfs_remove()` pins the filesystem, calls `simple_recursive_removal()`, and releases the pin.
- `remove_one()` invokes `__debugfs_file_removed()` for regular files.
- `__debugfs_file_removed()` pairs with `debugfs_file_get()`, drains active users, and runs registered cancellation callbacks until active operations finish.

Rename:
- `debugfs_change_name()` formats a new name, looks up the target, starts VFS rename locking, snapshots the old name, calls `d_move()`, and sends fsnotify move events.

## Important Dependencies

- `file.c` for protected debugfs file operations and removal coordination.
- VFS simple filesystem helpers.
- config through kernel boot parameter `debugfs=on|off|no-mount`.
- Security lockdown checks in setattr and file access paths.
- `d_make_persistent()`/`d_make_discardable()` from dcache for persistent debugfs dentries.

## Edge Cases and Risks

- When debugfs is disabled at boot, initialization returns `-EPERM` and create calls return errors.
- Callers are expected to tolerate failed debugfs creation; many APIs return error dentries intentionally.
- File removal must not free private data until all protected handlers have left.
- Mode/uid/gid changes are denied under kernel lockdown because file mode participates in debugfs lockdown heuristics.
- `debugfs_end_creating()` returns a borrowed persistent dentry; lifecycle differs from ordinary transient dentry references.
