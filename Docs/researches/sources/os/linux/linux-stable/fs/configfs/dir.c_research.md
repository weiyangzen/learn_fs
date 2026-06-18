# File Research: sources/os/linux/linux-stable/fs/configfs/dir.c

This file implements configfs directory behavior, config item/group attachment and detachment, dependency management, registration APIs, readdir, lookup, mkdir, and rmdir.

Key responsibilities:
- Maintains the configfs dirent tree under `configfs_dirent_lock`.
- Creates and removes configfs directories, attributes, default groups, and symlinks’ dirent linkage.
- Implements VFS inode operations for configfs directories and root directories.
- Implements configfs item/group lifecycle transitions for userspace-created and kernel-registered groups.
- Exports subsystem/group registration and dependency APIs.

Important control flow:
- Dirent creation:
  - `configfs_new_dirent()` allocates and inserts a dirent, rejecting insertion if parent is dropping.
  - Pinned children are added at the tail; unpinned attributes are added at the head so lookup can stop at pinned entries.
- Lookup:
  - `configfs_lookup()` only instantiates unpinned attribute files and refuses entries while parent hierarchy is still `CONFIGFS_USET_CREATING`.
- Item/group attach:
  - `configfs_attach_item()` creates a directory and populates attributes.
  - `configfs_attach_group()` additionally marks `CONFIGFS_USET_DIR` and recursively creates default groups.
  - `configfs_dir_set_ready()` clears `CONFIGFS_USET_CREATING` recursively after successful setup.
- Userspace mkdir:
  - `configfs_mkdir()` checks group operations, pins subsystem and new item modules, invokes `make_group()` or `make_item()`, links the object, attaches it to VFS, marks readiness, and rolls back on error.
- Userspace rmdir:
  - Rejects default groups.
  - Uses `configfs_symlink_mutex` plus `configfs_dirent_lock` to block symlink races.
  - Checks dependents and recursive emptiness/default-group state via `configfs_detach_prep()`.
  - Marks the fragment dead and detaches attributes/groups before unlinking object references.
- Dependency APIs:
  - `configfs_depend_item()` pins configfs, finds the subsystem dentry, and increments `s_dependent_count`.
  - `configfs_undepend_item()` decrements the dependency count.
  - `configfs_depend_item_unlocked()` handles cross-subsystem locking when called from callbacks.
- Registration APIs:
  - `configfs_register_subsystem()` links a subsystem under root and attaches its group.
  - `configfs_unregister_subsystem()` requires the subsystem directory to be empty and tears it down.
  - `configfs_register_group()`/`unregister_group()` handle kernel-created child groups.
- Directory iteration:
  - `configfs_dir_open()` creates a cursor dirent.
  - `configfs_readdir()` emits visible children and keeps cursor position stable using list movement.
  - `configfs_dir_lseek()` repositions the cursor.

Dependencies:
- Calls inode helpers from `inode.c`, attribute helpers from `file.c`, symlink helpers from `symlink.c`, and item reference helpers from `item.c`.
- Uses `configfs_pin_fs()` from `mount.c` for dependency and subsystem registration paths.
- Uses public configfs group/item callbacks from `struct config_item_type`.

Risks and invariants:
- Mutating dirent linkage requires the relevant inode lock plus `configfs_dirent_lock`, in that order.
- `CONFIGFS_USET_CREATING`, `CONFIGFS_USET_DROPPING`, and `CONFIGFS_USET_IN_MKDIR` prevent userspace and teardown races.
- Default groups require special lockdep depth handling to avoid false recursive inode-lock reports.
- `s_dependent_count` blocks rmdir while external kernel users depend on an item.
- Error handling is complex because VFS dentries/inodes may already be visible once partial attach succeeds.
