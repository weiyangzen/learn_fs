# File Research: sources/os/linux/linux/fs/configfs/configfs_internal.h

## Purpose
Defines configfs internal data structures, flags, shared locks, prototypes, and dentry-to-config object helper functions.

## Main Elements
- `struct configfs_fragment`: reference-counted fragment with rwsem and dead flag used to gate attribute access during teardown.
- `struct configfs_dirent`: internal tree node with refcount, children/sibling lists, link/dependent counters, element pointer, type flags, mode, dentry, optional persistent attributes, lockdep depth, and fragment pointer.
- Dirent flags: root/dir/item attributes/bin attributes/links/userspace-created dirs/default groups/dropping/in-mkdir/creating and pinned/not-pinned classes.
- Shared globals: `configfs_symlink_mutex`, `configfs_dirent_lock`, and `configfs_dir_cachep`.
- Cross-file prototypes for inode creation, dirent creation, file creation, mount pinning, symlink operations, and exported inode/file/dentry operations.
- Helpers: `to_item()`, `to_attr()`, `to_bin_attr()`, `configfs_get_config_item()`, dirent release, `configfs_get()`, and `configfs_put()`.

## Dependencies And Integration
This is the private contract for the configfs implementation. It links public `struct config_item`, `config_group`, and attribute APIs from `<linux/configfs.h>` to VFS dentries/inodes and internal dirents.

## Risk Notes
Dirent refcounting and fragment lifetime underpin nearly all configfs teardown safety. The pinned/not-pinned distinction affects lookup and readdir ordering, so flag misuse can make attributes invisible or incorrectly retained.
