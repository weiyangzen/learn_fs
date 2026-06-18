# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs_vnops.c

Read completely: 1587 lines.

## Role

This file implements dirfs vnode operations. It maps DragonFly VFS/namecache operations onto host filesystem syscalls for a mounted host directory, while using DragonFly's vnode, buffer-cache, VM, kqueue, advisory-lock, and namecache infrastructure.

## Main Responsibilities

- Namecache and creation operations:
  - `dirfs_nresolve()` resolves children from the passive fd cache or creates a new dirfs node through host stat.
  - `dirfs_ncreate()` creates host regular files with `openat(O_CREAT | O_RDWR)`.
  - `dirfs_nmkdir()` creates host directories with `mkdirat()`.
  - `dirfs_nsymlink()` creates host symlinks with `symlink()`.
  - `dirfs_nremove()` removes host non-directories with `unlinkat()`.
  - `dirfs_nrmdir()` removes host directories with `rmdir()`.
  - `dirfs_nrename()` renames host paths with `rename()` and updates namecache/node state.
  - `dirfs_nlookupdotdot()`, `dirfs_nmknod()`, and `dirfs_nlink()` are unsupported.
- Open/close:
  - `dirfs_open()` opens host fds for non-root nodes as needed.
  - `dirfs_close()` syncs regular-file buffers and runs standard vnode close accounting.
- Permissions and attributes:
  - `dirfs_access()` checks mount read-only state and helper permissions.
  - `dirfs_getattr()` refreshes host stat data and fills `vattr`.
  - `dirfs_setattr()` handles flags, size, ownership, mode, and timestamps through dirfs helper functions.
  - `dirfs_fsync()` flushes DragonFly buffers and host fd state.
- Regular-file I/O:
  - `dirfs_read()` reads through the buffer cache with `getcacheblk()`/`bread()` and `uiomovebp()`.
  - `dirfs_write()` enforces file-size limits, handles append, extends host file/buffer state, writes through cached buffers, and schedules dirty writes.
  - `dirfs_strategy()` translates buffer-cache I/O to host `pread()`/`pwrite()`.
  - `dirfs_bmap()` implements identity logical-to-device offset mapping for the synthetic backing.
- Directory and symlink reads:
  - `dirfs_readdir()` uses host `getdirentries()` and writes VFS dirents to the caller.
  - `dirfs_readlink()` reads symlink text with `readlinkat()`.
- Lifecycle:
  - `dirfs_inactive()` recycles unlinked nodes or adds nodes with fds to the passive fd cache.
  - `dirfs_reclaim()` detaches vnode/node association.
- Eventing and locks:
  - `dirfs_advlock()` uses `lf_advlock()`.
  - `dirfs_kqfilter()` supports read, write, and vnode filters.
  - Filter callbacks report readable bytes, write readiness, vnode flags, and revoke EOF.
- Defines `dirfs_vnode_vops`.

## Synchronization and Lifetime Model

- Node-level operations use `dirfs_node_lock()` where parent/node fd or metadata state needs serialization.
- Mount token use appears around some namecache operations that fetch and release target vnodes.
- Passive fd cache lookups in `dirfs_nresolve()` scan `dm_fdlist` for child nodes that can be reactivated.
- Vnode reclaim calls `dirfs_free_vp()`, which may drop the final node reference and free the node.
- Buffer-cache strategy assumes regular-file nodes have an open host fd and panics if missing.

## Important Interactions

- Calls support routines from `dirfs_subr.c` for node allocation, stat refresh, fd/path resolution, host opens, passive cache management, and attribute changes.
- Uses host functions/syscalls:
  - `openat()`
  - `mkdirat()`
  - `unlinkat()`
  - `rename()`
  - `rmdir()`
  - `symlink()`
  - `getdirentries()`
  - `readlinkat()`
  - `pread()`
  - `pwrite()`
  - `lseek()`
- Uses VFS/cache helpers:
  - `cache_setvp()`
  - `cache_setunresolved()`
  - `cache_unlink()`
  - `cache_rename()`
  - `cache_inval_vp()`
  - `vop_write_dirent()`
  - `vfsync()`
  - `bread()`
  - `bdwrite()`/`bwrite()`
  - `biodone()`

## Notable Design Details

- Regular-file reads and writes go through DragonFly's buffer cache rather than direct host `read()`/`write()` from VOP read/write.
- Host `pread()`/`pwrite()` happens in `dirfs_strategy()`, making buffer-cache writeback the actual host persistence path.
- Namecache is updated explicitly after create, remove, rename, mkdir, rmdir, and symlink operations.
- `dirfs_nrename()` updates the renamed node's cached name and marks an overwritten target as unlinked/destroyed.
- `dirfs_readdir()` relies on host directory offsets from `getdirentries()`/`lseek()`.

## Research Notes

- `dirfs_ncreate()` computes a write-permission error but then calls `dirfs_alloc_file()` regardless, which may overwrite the intended `EPERM`.
- `dirfs_getattr()` returns `0` even if `dirfs_node_stat()` failed, while only filling attributes on success.
- `dirfs_fsync()` calls `fsync()` twice on failure and returns `0` regardless of the collected error.
- `dirfs_readlink()` passes `nlen + 1` to `uiomove()` after setting the NUL terminator after the move; symlink read APIs normally return bytes without a trailing NUL.
- The code is designed for vkernel use and depends on host libc/syscall behavior being available in the kernel-virtual environment.
