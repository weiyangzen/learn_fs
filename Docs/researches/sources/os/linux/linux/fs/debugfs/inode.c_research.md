# File Research: sources/os/linux/linux/fs/debugfs/inode.c

## Role

Implements debugfs filesystem registration, mount context handling, inode allocation, creation/removal APIs, rename support, and persistent dentry integration.

## Major Responsibilities

- Registers the `debugfs` filesystem and `/sys/kernel/debug` mount point.
- Parses mount options: `uid`, `gid`, `mode`, and `source`.
- Creates files, directories, automount points, and symlinks.
- Recursively removes debugfs trees while coordinating with active file users.
- Renames debugfs dentries.
- Applies lockdown restrictions to setattr changes.

## Mount and Superblock Behavior

Debugfs is a single-instance filesystem using `get_tree_single()`.

`debugfs_fill_super()`:

- Calls `simple_fill_super()` with `DEBUGFS_MAGIC`.
- Sets super operations.
- Installs default dentry operations.
- Marks superblock dentries with `DCACHE_DONTCACHE`.
- Applies root mode/uid/gid options.

Default root mode is `0700`.

Mount options are stored in `struct debugfs_fs_info`.

`debugfs_reconfigure()` syncs the filesystem, copies new options into the superblock state, and applies remount options conditionally.

## Lockdown Behavior

`debugfs_setattr()` blocks mode, uid, or gid changes when `security_locked_down(LOCKDOWN_DEBUGFS)` denies them. This preserves debugfs lockdown heuristics based on file permissions.

## Inode Cache

Debugfs has a private inode cache containing `struct debugfs_inode_info`.

`debugfs_alloc_inode()` allocates from this cache.

`debugfs_free_inode()` frees symlink targets and returns the inode wrapper to the slab cache.

The wrapper stores:

- Real fops or short fops.
- Automount callback.
- Auxiliary pointer.

## Dentry Operations

Default dentry ops include:

- `.d_release = debugfs_release_dentry`
- `.d_automount = debugfs_automount`

`debugfs_release_dentry()` frees `debugfs_fsdata` and validates that cancellation lists are empty.

`debugfs_automount()` dispatches to the per-inode automount callback.

## Creation Flow

`debugfs_start_creating()`:

- Rejects creation when debugfs is disabled or unregistered.
- Pins the debugfs filesystem with `simple_pin_fs()`.
- Defaults parent to the debugfs root.
- Calls `simple_start_creating()`.

`debugfs_failed_creating()` completes creation cleanup and releases the filesystem pin.

`debugfs_end_creating()` completes creation and returns a borrowed dentry.

`__debugfs_create_file()` creates regular files, sets inode private data, installs proxy fops, records raw fops/aux data, persists the dentry with `d_make_persistent()`, and sends fsnotify create events.

Public file constructors:

- `debugfs_create_file_full()`
- `debugfs_create_file_short()`
- `debugfs_create_file_unsafe()`
- `debugfs_create_file_size()`

## Directory, Automount, and Symlink Creation

`debugfs_create_dir()` creates a simple directory inode, increments parent link count, persists the dentry, and sends mkdir notification.

`debugfs_create_automount()` creates an automount directory with `S_AUTOMOUNT` and stores an automount callback.

`debugfs_create_symlink()` duplicates the target path, creates a symlink inode, assigns `simple_get_link`, and persists the dentry.

## Lookup and Removal

`debugfs_lookup()` returns a referenced positive dentry under a parent or root using `lookup_noperm_positive_unlocked()`.

`debugfs_remove()` recursively removes a debugfs subtree with `simple_recursive_removal()`.

For regular files, removal calls `__debugfs_file_removed()`:

- Pairs memory ordering with lazy fsdata installation in `debugfs_file_get()`.
- Drops the active user ref.
- Cancels registered cancellation entries.
- Waits for active users to drain.

`debugfs_lookup_and_remove()` combines lookup, recursive removal, and `dput()`.

## Rename

`debugfs_change_name()` formats a new name, looks up a target, uses VFS rename helpers, snapshots the old dentry name, updates timestamps, moves the dentry with `d_move()`, sends fsnotify move, and releases references.

Rename uses `RENAME_NOREPLACE` and treats renaming to itself as success.

## Initialization and Enablement

`debugfs_enabled` defaults from `CONFIG_DEBUG_FS_ALLOW_ALL` and can be controlled by early parameter `debugfs=on`, `debugfs=off`, or deprecated `debugfs=no-mount`.

`debugfs_init()`:

- Skips registration when disabled.
- Creates `/sys/kernel/debug`.
- Creates the debugfs inode cache.
- Registers the filesystem.
- Marks debugfs initialized.

## Important Invariants

- Debugfs creation pins the filesystem; removal releases those pins.
- Created debugfs dentries are persistent and must be removed explicitly.
- Debugfs callers are expected to ignore creation failures in many driver paths.
- No automatic cleanup occurs on module unload.
- `dentry->d_fsdata` is used by file lifetime protection and freed at dentry release.

## Research Notes

This file ties debugfs into VFS simple filesystem infrastructure and depends heavily on `dcache.c` persistent dentry behavior. The most important correctness surfaces are creation/removal reference accounting and removal waiting for active file operations.
