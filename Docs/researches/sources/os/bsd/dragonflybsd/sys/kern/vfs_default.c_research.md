# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_default.c

This file defines default vnode and VFS operations plus compatibility shims that translate DragonFly's newer namecache-based `VOP_N*` API into older namei-style vnode operations for filesystems that have not implemented the new API directly.

`default_vnode_vops` supplies defaults for vnode operations. Most unsupported operations return `EOPNOTSUPP`, `EINVAL`, or `ENOTTY`; selected operations use standard implementations such as `vop_stdopen`, `vop_stdclose`, `vop_stdgetattr_lite`, `vop_stdpathconf`, `vop_stdioctl`, `vop_stdfdatasync`, `vop_stdmarkatime`, `vop_stdallocate`, and `vop_stdmountctl`. New namecache operations default to compatibility wrappers like `vop_compat_nresolve`, `vop_compat_ncreate`, `vop_compat_nremove`, and `vop_compat_nrename`.

Simple default error/null helpers:
- `vop_eopnotsupp`, `vop_ebadf`, `vop_enotty`, `vop_einval`, `vop_null`, and `vop_defaultop`.
- `vop_nolookup` returns `ENOTDIR`.
- `vop_nostrategy` reports missing strategy, marks the buffer with `B_ERROR`, sets `EOPNOTSUPP`, and completes the bio.

Compatibility namecache API:
- `vop_compat_nresolve` resolves a locked namecache entry by calling old lookup on the parent directory vnode, then uses `cache_setvp` for positive or negative results and records whiteout state.
- `vop_compat_nlookupdotdot` performs old `".."` lookup for NFS/namecache topology reconstruction.
- `vop_compat_ncreate`, `vop_compat_nmkdir`, `vop_compat_nmknod`, and `vop_compat_nsymlink` perform old CREATE lookup expecting `EJUSTRETURN`, then call the corresponding old create operation and update the locked ncp.
- `vop_compat_nlink` creates a hardlink target, using `CNP_NOTVP` to avoid source/target vnode alias issues.
- `vop_compat_nwhiteout` translates create/delete/lookup whiteout operations.
- `vop_compat_nremove` performs old DELETE lookup, rejects directories, calls old remove, and marks the ncp destroyed via `cache_unlink`.
- `vop_compat_nrmdir` validates directory removal constraints, calls old rmdir, invalidates the ncp and vnode on success.
- `vop_compat_nrename` performs old delete lookup for the source and old rename lookup for the target, then calls old rename and updates topology through `cache_rename`.

Standard vnode operations:
- `vop_stdpathconf` returns POSIX constants for common `_PC_*` names.
- `vop_stdopen` initializes file object type/ops/data, takes a vnode ref, increments write/open counts.
- `vop_stdclose` decrements write/open counts with assertions.
- `vop_stdgetattr_lite` derives `vattr_lite` from full `VOP_GETATTR`.
- `vop_stdgetpages` and `vop_stdputpages` delegate to generic vnode pager routines when a mount exists.
- `vop_stdnoread` and `vop_stdnowrite` return `EINVAL`.
- `vop_stdfdatasync` delegates to `VOP_FSYNC_FP`.

Mount control and allocation:
- `vop_stdmountctl` returns visible mount flags as a string or delegates journal operations to `journal_mountctl`.
- `vop_stdallocate` implements a generic fallocate-like operation by validating/growing size with `VOP_SETATTR`, then reading existing regions or zero-filling and writing blocks across the requested range. It updates `a_offset` and `a_len` to reflect progress.
- `vop_stdioctl` implements default `FIOSEEKDATA`/`FIOSEEKHOLE` behavior for regular files, treating data as present until EOF and hole at file size.

Default VFS operations:
- `vfs_stdroot`, `vfs_stdstatfs`, `vfs_stdvptofh`, `vfs_stdquotactl`, `vfs_stdvget`, `vfs_stdfhtovp`, `vfs_stdcheckexp`, `vfs_stdnosync`, and `vfs_stdextattrctl` return unsupported.
- `vfs_stdstart`, `vfs_stdsync`, `vfs_stdinit`, and `vfs_stduninit` succeed without action.
- `vfs_stdstatvfs` calls `VFS_STATFS` and converts `statfs` fields to `statvfs`.
- `vfs_stdac_init` enables quota/accounting support through `vq_init` for selected filesystem type names.
- `vfs_stdac_done` calls `vq_done`.
- `vfs_stdncpgen_set` and `vfs_stdncpgen_test` are no-op defaults for mount namecache generation support.
- `vfs_stdmodifying` enforces read-only mount behavior by returning `EROFS`.

Notable dependencies include old and new vnode operation interfaces, namecache APIs from `vfs_cache.c`, vnode locking/refcounting, `componentname`, buffer/bio completion, VM vnode pager, mount flags, journal mountctl, quota accounting, and statfs/statvfs compatibility.

Implementation risks for future changes:
- Compatibility wrappers intentionally lock parent directory vnodes exclusively because older filesystems may store lookup side effects in inode state.
- Old lookup may return parent-directory lock state through `CNP_PDIRUNLOCK`; each wrapper must release exactly according to that flag.
- Namecache updates after old operations are required for correctness. Missing `cache_setvp`, `cache_unlink`, `cache_inval`, or `cache_rename` calls would desynchronize old vnode behavior from the new topology.
- `vop_compat_nrename` is especially sensitive because old rename consumes/release semantics differ for source and target vnodes.
