# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.h

## Role

Kernel-facing declaration header for the generic filesystem helper routines implemented mainly in `fs_subr.c`.

## Main Contents

- Declares default vnode/VFS operations such as `fs_nosys`, `fs_inval`, `fs_sync`, `fs_fsync`, `fs_putpage`, `fs_ioctl`, `fs_rwlock`, `fs_cmp`, `fs_seek`, `fs_poll`, and `fs_pathconf`.
- Declares page disposal helpers `fs_dispose()` and `fs_nodispose()`.
- Declares ACL/share helpers `fs_fab_acl()`, `fs_shrlock()`, and `fs_acl_nontrivial()`.
- Declares vnode event support stubs `fs_vnevent_nosupport()` and `fs_vnevent_support()`.
- Declares `fs_need_estale_retry()`, antivirus scan registration/callout functions, and `fs_vfsp_global()`.
- Declares `fs_reject_epoll()` for filesystems that need to reject epoll use in custom `VOP_POLL` handlers.

## Dependencies And Interactions

- Pulls in vnode, vfs, credential, poll, page, ACL, share, and flock types.
- Guarded for `_KERNEL` or `_FAKE_KERNEL`; provides C++ linkage guards.
