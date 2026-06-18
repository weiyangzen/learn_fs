# File Research: sources/os/linux/linux/fs/proc/inode.c

## Scope

This file implements procfs inode allocation, eviction, superblock operations, proc directory entry lifetime protection, regular proc file dispatch, symlink handling, and conversion from `struct proc_dir_entry` metadata into live VFS inodes.

## Public And Internal APIs Covered

- Proc inode cache setup: `proc_init_kmemcache()`.
- Superblock operations: `proc_sops`.
- Dentry invalidation helper: `proc_invalidate_siblings_dcache()`.
- Proc entry rundown: `proc_entry_rundown()`.
- Inode construction: `proc_get_inode()`.
- Symlink inode operations: `proc_link_inode_operations`.
- File operation tables for read, read_iter, compat ioctl, mmap, poll, llseek, open, and release dispatch.

## Control Flow And Behavior

- `proc_alloc_inode()` allocates `struct proc_inode` from `proc_inode_cachep` and initializes PID, fd, PDE, sysctl, namespace, and sibling-inode state.
- `proc_evict_inode()` truncates page cache, clears the VFS inode, evicts process-associated proc inodes, and delegates sysctl inode teardown to `proc_sys_evict_inode()`.
- `proc_free_inode()` releases the cached PID and associated PDE reference before freeing the proc inode object.
- `proc_show_options()` reports non-default proc mount options: `gid=`, `hidepid=`, and `subset=pid`.
- `proc_invalidate_siblings_dcache()` walks a sysctl/PDE sibling inode hlist under RCU, removes each inode from the list, safely pins the superblock/inode, and invalidates aliases so removed or namespace-sensitive proc entries stop resolving from stale dentries.
- Dynamic PDE access is protected with the `in_use` atomic. `use_pde()` refuses entries being removed; `unuse_pde()` completes removal waiters when the biased count drains.
- `proc_entry_rundown()` marks a PDE as unloading, waits for active method calls to finish, then closes tracked openers with custom release hooks.
- `proc_reg_open()` disables llseek when a PDE lacks seek support, pins non-permanent PDEs during open, and tracks files with custom `proc_release` hooks in `pde_openers`.
- `proc_reg_release()` either calls permanent PDE release directly or finds the tracked opener and uses `close_pdeo()` so module removal and final close race safely.
- `proc_get_inode()` builds a VFS inode from PDE mode, ownership, size, nlink, and operation pointers. Regular files select read-iter vs read file ops and compat variants when available; directories use PDE directory ops; symlinks use PDE inode ops.

## Dependencies

- Uses `internal.h` definitions for `struct proc_inode`, `struct proc_dir_entry`, `pde_opener`, `PDE()`, and `PROC_I()`.
- Coordinates with pid proc support via `proc_pid_evict_inode()`.
- Coordinates with `/proc/sys` via `proc_sys_evict_inode()`.
- Relies on VFS inode, dcache, superblock, file operation, RCU, spinlock, completion, and slab APIs.

## Risks And Invariants

- Non-permanent PDE methods must only run while `use_pde()` holds the entry active; otherwise module-backed operation tables could disappear.
- `close_pdeo()` is designed for at most two concurrent contexts: final close and PDE deletion. Its `closing` flag and completion prevent duplicate `proc_release()` calls.
- Superblock active references in `proc_invalidate_siblings_dcache()` prevent alias invalidation from racing unmounted proc instances.
- `proc_get_inode()` assumes PDE type is regular, directory, or symlink; any other mode triggers `BUG()`.
