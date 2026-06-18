# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nbmlock.c

Provides common top-level helpers for non-blocking mandatory locking, NBMAND share/lock conflict checks, and System V mandatory lock detection.

Key elements:
- `nbl_start_crit()` and `nbl_end_crit()` enter/leave `vp->v_nbllock`, coordinating I/O paths with lock/share state changes.
- `nbl_in_crit()` reports whether the vnode NBMAND lock is held; comments restrict it to assertion-style use.
- `nbl_need_check()` currently checks whether the vnode’s VFS has `VFS_NBMAND` enabled.
- `nbl_conflict()` is the top-level conflict checker. It requires callers to already be in the NBMAND critical region, checks share reservation conflicts first via `nbl_share_conflict()`, skips byte-range lock checks for remove/rename, and otherwise calls `nbl_lock_conflict()`.
- `nbl_svmand()` detects System V mandatory locking mode bits by fetching `AT_MODE`; when the filesystem supports ACE mask-on-access, it passes `ATTR_NOACLCHECK` to avoid redundant ACL/kidmap work in read/write paths.

Dependencies:
- Vnode state: `vnode_t::v_nbllock`, `v_vfsp`, `vfs_flag`.
- NBMAND lower-level helpers declared in `sys/nbmlock.h`: `nbl_share_conflict()` and `nbl_lock_conflict()`.
- VFS and vnode APIs: `VFS_NBMAND`, `vfs_has_feature()`, `VFSFT_ACEMASKONACCESS`, `VOP_GETATTR()`, `MANDLOCK()`.

Research notes:
- The file is intentionally small and policy-oriented: it centralizes when to ask lower-level lock/share logic rather than implementing byte-range conflict scanning itself.
- `svmand` in `nbl_conflict()` broadens record-lock checking for System V mandatory locking so I/O can fail instead of blocking behind a lock-release path and risking deadlock.
