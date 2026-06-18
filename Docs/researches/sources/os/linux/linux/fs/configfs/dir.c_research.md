# File Research: sources/os/linux/linux/fs/configfs/dir.c

## Purpose
Implements configfs directory tree management: dirent allocation/linkage, item/group attach and detach, mkdir/rmdir, default groups, dependency pins, directory iteration, and subsystem/group registration APIs.

## Main Elements
- Global locking: `configfs_dirent_lock` protects dirent linkage, symlink linkage, dropping flags, and traversal state; `configfs_subsystem_mutex` serializes root-level subsystem link/unlink when no parent subsystem exists.
- Dentry cleanup: `configfs_d_iput()` clears `sd->s_dentry` only for the dying dentry and drops dirent references.
- Fragment lifecycle: `new_fragment()`, `get_fragment()`, and `put_fragment()` provide teardown coordination with attribute files.
- Dirent creation/removal: `configfs_new_dirent()`, `configfs_make_dirent()`, `configfs_remove_dirent()`, `configfs_dirent_exists()`, and ready-state helpers manage internal tree nodes.
- Directory creation and lookup: `configfs_create_dir()` creates item directories; `configfs_lookup()` lazily instantiates attribute files and hides unready attaching hierarchies.
- Attach/detach flows: `configfs_attach_item()`, `configfs_attach_group()`, `configfs_detach_item()`, `configfs_detach_group()`, `detach_attrs()`, and `detach_groups()` populate/remove attributes and default groups.
- Default groups: `create_default_group()`, `populate_groups()`, and `configfs_remove_default_groups()` fake mkdir for kernel-created default children and mark them default.
- Hierarchy links: `link_obj()`, `unlink_obj()`, `link_group()`, and `unlink_group()` maintain `ci_parent`, `ci_group`, `cg_children`, and subsystem pointers with config-item references.
- Dependency APIs: `configfs_depend_item()`, `configfs_depend_item_unlocked()`, and `configfs_undepend_item()` prevent external users from racing item removal by incrementing dirent dependent counts.
- VFS mkdir/rmdir: `configfs_mkdir()` calls client `make_group()` or `make_item()`, links the object, pins module owners, attaches VFS nodes, and rolls back on error; `configfs_rmdir()` rejects default groups, checks dependents/links, marks fragments dead, detaches VFS state, and calls client cleanup callbacks.
- Directory operations: open/close allocate a cursor dirent; `configfs_readdir()` emits live entries while maintaining cursor position; `configfs_dir_lseek()` repositions the cursor.
- Registration APIs: `configfs_register_group()`, `unregister_group()`, `register_default_group()`, `unregister_default_group()`, `register_subsystem()`, and `unregister_subsystem()` create/remove kernel-driven groups and top-level subsystems.

## Dependencies And Integration
This is the core of configfs and integrates with `file.c` for attribute files, `inode.c` for inode allocation/attributes, `symlink.c` for link operations, `mount.c` for filesystem pinning, module refcounts, VFS locking, fsnotify, and public configfs client callbacks.

## Risk Notes
The highest-risk code is mkdir/rmdir interaction with default group population, symlink creation, dependency pins, and fragment death. Lock ordering spans inode rwsems, `configfs_symlink_mutex`, subsystem mutexes, and `configfs_dirent_lock`; mistakes can deadlock or allow teardown while callbacks are active. Error rollback after partially attached groups must undo both VFS and config-item references.
