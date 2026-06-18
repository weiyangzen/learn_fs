# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_subr.c

## Role

This is DragonFly BSD's main VFS support file for vnode lifecycle, vnode-buffer association, buffer flush/truncation/sync logic, device vnode aliasing, mount export state, timestamp/attribute helpers, and mount-wide VM page synchronization. It provides the shared machinery that filesystem implementations and syscall paths rely on rather than a single filesystem-specific policy.

## Main Responsibilities

- Initializes VFS-wide vnode sizing in `vfs_subr_init()`, deriving `maxvnodes` from physical memory, `maxproc`, KVA size, and hard min/max bounds.
- Provides common attribute and timestamp helpers via `vfs_timestamp()` and `vattr_null()`, with sysctl-controlled timestamp precision.
- Maintains per-vnode buffer-cache red-black trees:
  - `v_rbhash_tree` for lookup by logical offset.
  - `v_rbclean_tree` and `v_rbdirty_tree` for clean/dirty ownership.
  - `bgetvp()`, `brelvp()`, and `reassignbuf()` attach, detach, and move buffers between trees.
- Implements vnode buffer invalidation, truncation, and flushing:
  - `vinvalbuf()` flushes/invalidates all buffers and optionally persists dirty state first.
  - `vtruncbuf()` destroys buffers beyond EOF and synchronizes remaining metadata.
  - `vfsync()` performs lazy, async, and synchronous multipass dirty-buffer writeback.
- Handles vnode reclamation and revocation:
  - `vclean_vxlocked()` disassociates a vnode from its filesystem, invalidates namecache entries, flushes buffers, deactivates if needed, destroys/deallocates VM objects, and calls `VOP_RECLAIM()`.
  - `vgone_vxlocked()`, `vclean_unlocked()`, `vrecycle()`, and `vrevoke()` build higher-level reclaim/revoke behavior.
- Creates and manages special/device vnodes with `bdevvp()`, `v_associate_rdev()`, `v_release_rdev()`, `addaliasu()`, `count_dev()`, and `vcount()`.
- Initializes vnode VM backing objects in `vinitvmio()`.
- Provides generic permission checking in `vaccess()`.
- Implements VFS sysctl exposure for filesystem configuration records.
- Builds and tears down NFS export address lists using radix trees in `vfs_export()`, `vfs_hang_addrlist()`, `vfs_free_addrlist()`, `vfs_setpublicfs()`, and `vfs_export_lookup()`.
- Performs mount-wide VM page cleaning through `vfs_msync()`.
- Provides miscellaneous VFS helpers: `vfs_unmountall()`, `vfs_flagstostr()`, `vn_gone()`, `vn_todev()`, `vn_isdisk()`, `vn_get_namelen()`, `vop_write_dirent()`, `vn_mark_atime()`, `vfs_inodehashsize()`, and `init_va_filerev()`.

## Synchronization and Lifetime Model

- Per-vnode buffer tree operations are protected by `vp->v_token`.
- Special-device alias lists are protected by the static `spechash_token`.
- Reclamation requires a VX-locked and referenced vnode for `vgone_vxlocked()` and `vclean_vxlocked()`.
- Buffer scans use `RB_SCAN()` callbacks that lock each buffer, revalidate it after the lock, and tolerate races by looping until no matching buffers remain.
- Dirty-buffer transitions integrate with the per-mount syncer: `reassignbuf()` adds dirty vnodes to the syncer worklist and removes them when dirty buffers and dirty vnode flags are gone.
- VM object destruction is careful about object references and pager deallocation; reclaimed vnodes must leave `VOBJBUF` and `VOBJDIRTY` cleared.

## Notable Design Details

- `vinvalbuf()` first waits for tracked writes and runs `VOP_FSYNC()` when `V_SAVE` is requested, then drains clean and dirty buffer trees, waits for write I/O and paging-in-progress, and finally removes VM pages.
- `vfsync()` distinguishes data and metadata by negative logical offsets; synchronous mode uses multiple passes and escalates dependency flushing on the final pass.
- `bgetvp()` can perform invasive overlap checks controlled by `vfs.check_buf_overlap`, useful for debugging filesystems that instantiate overlapping buffers.
- `vclean_vxlocked()` sets `VRECLAIMED` early as an interlock, invalidates namecache aliases, flushes buffers twice around deactivate, and moves the vnode to dead vnode ops.
- `vfs_msync()` uses `vsyncscan()` for filesystems with `MNTK_THR_SYNC`, otherwise scans all mount vnodes, cleaning `VOBJDIRTY` VM objects while respecting `MNTK_NOMSYNC` and `MAP_NOSYNC` semantics where appropriate.

## Cross-File Relationships

- `vfs_sync.c` consumes `VONWORKLST`, `VISDIRTY`, `VOBJDIRTY`, and syncer callbacks used by `reassignbuf()`, `vclrobjdirty()`, and `vfs_msync()`.
- `vfs_syscalls.c` calls helpers such as `vinvalbuf()`, `vfs_msync()`, `vfs_unmountall()`-related unmount logic, `vaccess()` indirectly through VOPs, `vcount()`, `vrevoke()`, `vn_writechk()`-adjacent routines, `vfs_flagstostr()`, and NFS filehandle/export helpers.
- `vfs_vm.c` is the newer VM/buffer coherency path for truncation and extension; `vfs_subr.c` retains the older `vtruncbuf()` path.
- `vfs_vfsops.c` wraps filesystem VFS operations that this file invokes through macros such as `VFS_ROOT()`, `VFS_SYNC()`, `VFS_VPTOFH()`, and `VFS_STATFS()`.

## Research Notes

- This file is core infrastructure, not optional glue. Bugs here affect all filesystems using DragonFly's vnode, buffer-cache, mount, and VM integration contracts.
- The high-risk areas are lock ordering and revalidation in buffer scans, vnode reclamation while references still exist, forced unmount cleanup, and NFS export radix-list lifetime.
- The file exposes several diagnostic sysctls (`debug.numvnodes`, `debug.verbose_reclaims`, `vfs.reassignbufcalls`, `vfs.check_buf_overlap`, `kern.maxvnodes`, `vfs.timestamp_precision`) that are useful when investigating VFS behavior.
