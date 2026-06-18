# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fs_subr.c

## Role

Provides generic vnode/VFS helper routines used by many filesystems: default operation stubs, locking/share wrappers, pathconf defaults, ACL fabrication, reparse-point kernel helpers, antivirus hook registration, and global pseudo-vfs construction.

## Main Behavior

- Defines common default operations: `fs_nosys()`, `fs_inval()`, `fs_notdir()`, `fs_sync()`, `fs_syncfs_nop()`, `fs_fsync()`, `fs_putpage()`, `fs_ioctl()`, `fs_rwlock()`, `fs_rwunlock()`, `fs_cmp()`, `fs_seek()`, `fs_setfl()`.
- `fs_frlock()` translates `fcntl` lock commands to reclock flags, handles remote/PXFS/OFD restrictions, supports NBMAND validation, serializes locks with `nbl_start_crit()`, and uses callback wrapping for blocking serialized locks.
- `fs_poll()` returns immediate readiness for regular filesystem polling, but rejects epoll and edge-triggered poll use with `EPERM` through `fs_reject_epoll()`.
- `fs_pathconf()` supplies defaults for link/path/name limits, pipe buffer, truncation, chown restriction, large-file bits, ACL support, case behavior, system attributes, and access filtering.
- `fs_dispose()` frees or destroys pages; `fs_nodispose()` panics if incorrectly invoked.
- `fs_fab_acl()` fabricates trivial ACLENT or ACE ACLs from mode/uid/gid for filesystems without native ACLs.
- `fs_shrlock()` implements common DOS share reservation handling and NBMAND validation.
- `fs_acl_nontrivial()` probes supported ACL styles and determines whether ACLs are nontrivial.
- `fs_need_estale_retry()` bounds retry attempts using tunable `fs_estale_retry`.

## Reparse Support

- `reparse_vnode_parse()` reads symlink data into a kernel buffer and parses it as reparse nvlist data.
- `reparse_point_init()` initializes door locking.
- `reparse_kderef()` builds `svc_type:svc_data`, calls the reparsed daemon via kernel door upcall, retries `EAGAIN`/`EINTR`, resets/reopens stale door handles on `EBADF`, handles `EOVERFLOW`, and copies returned service data into the caller buffer.

## Other Interfaces

- `fs_vscan_register()` installs an antivirus scan callback; `fs_vscan()` invokes it for regular files.
- `fs_vfsp_global()` builds an immortal pseudo-filesystem `vfs_t` for subsystems such as sockfs/fifofs that do not mount normally.

## Dependencies And Interactions

- Uses kernel vnode, lock manager, share reservation, ACL, door, nbmlock, pathname, and poll internals.
- Provides prototypes through `fs_subr.h`.
