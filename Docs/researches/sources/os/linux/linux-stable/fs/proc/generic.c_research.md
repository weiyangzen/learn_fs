# File Research: sources/os/linux/linux-stable/fs/proc/generic.c

## Purpose

Provides generic procfs directory/file registration, lookup, readdir, inode metadata, creation helpers, removal helpers, and simple write support.

## Main Responsibilities

- Proc directory entry storage:
  - Maintains subdirectories in red-black trees protected by `proc_subdir_lock`.
  - `pde_subdir_find()`, `pde_subdir_insert()`, `pde_subdir_first()`, and `pde_subdir_next()` manage lookup/order.
- Entry allocation and lifetime:
  - `proc_alloc_inum()`/`proc_free_inum()` allocate dynamic proc inode numbers.
  - `pde_free()` frees names, symlink targets, and the slab object.
  - `pde_put()` drops references and frees entries.
- Generic lookup/readdir:
  - `proc_lookup_de()` finds PDEs and builds VFS inodes.
  - `proc_lookup()` respects `pidonly` proc mounts.
  - `proc_readdir_de()` emits entries from the PDE rb-tree.
  - `proc_readdir()` also respects `pidonly`.
- Directory/file inode operations:
  - `proc_setattr()` applies setattr and reflects uid/gid/mode into PDE metadata.
  - `proc_getattr()` refreshes nlink from PDE before generic stat fill.
  - `proc_dir_operations` and `proc_dir_inode_operations`.
- Proc registration:
  - `proc_register()` assigns inode number, sets permanent/read/lseek flags, inserts into parent tree, and updates nlink.
  - `__proc_create()` validates paths/names, resolves parent path components, rejects numeric names directly under `/proc`, allocates PDEs, initializes metadata, and inherits forced lookup flags.
- Creation helpers:
  - `proc_symlink()`
  - `_proc_mkdir()`, `proc_mkdir_data()`, `proc_mkdir_mode()`, `proc_mkdir()`
  - `proc_create_mount_point()`
  - `proc_create_reg()`, `proc_create_data()`, `proc_create()`
  - `proc_create_seq_private()`
  - `proc_create_single_data()`
  - `proc_set_size()` and `proc_set_user()`
- Removal helpers:
  - `remove_proc_entry()` removes one entry, runs down users, warns if non-empty.
  - `remove_proc_subtree()` removes a full subtree with permanent-entry checks.
  - `proc_remove()` wraps subtree removal for a PDE.
- Misc support:
  - `proc_get_parent_data()` retrieves parent private data.
  - `proc_simple_write()` copies a bounded user buffer and calls a PDE write callback.

## Key Data/Control Flow

- Names with path components are resolved by `__xlate_proc_name()`.
- Entries under parents marked `PROC_ENTRY_FORCE_LOOKUP` inherit force lookup behavior, important for `/proc/<pid>/net`.
- Dentry operations differ:
  - Generic proc entries use `proc_misc_dentry_ops`, which invalidates removed PDEs.
  - Forced lookup/net entries use `proc_net_dentry_ops`, which forces revalidation/deletion.
- Seq and single proc helpers wrap kernel `seq_file` APIs into `struct proc_ops`.

## Concurrency and Lifetime Notes

- `proc_subdir_lock` protects the PDE tree.
- `pde_get()`/`pde_put()` protect entries while lookup/readdir drop the tree lock.
- Removal calls `proc_entry_rundown()` before dropping final references to wait for active users.
- Permanent entries cannot be removed and trigger warnings.
