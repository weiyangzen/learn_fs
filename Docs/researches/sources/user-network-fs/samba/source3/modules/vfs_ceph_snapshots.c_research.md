# sources/user-network-fs/samba/source3/modules/vfs_ceph_snapshots.c

## Purpose
`vfs_ceph_snapshots.c` exposes CephFS snapshots as SMB Previous Versions while remaining independent from the Ceph userspace VFS module. It works on kernel-mounted CephFS shares by discovering Ceph's per-directory snapshot namespace, defaulting to `.snap`, and translating SMB time-warped `@GMT` requests into backing snapshot paths.

## Important APIs, Types, And Functions
The module registers `ceph_snap_fns` as `ceph_snapshots`. Key hooks are `get_shadow_copy_data_fn`, read path translation wrappers (`stat`, `lstat`, `openat`, `chdir`, `readlinkat`, `realpath`, `get_real_filename_at`) and write guards (`renameat`, `linkat`, `symlinkat`, `unlinkat`, `mkdirat`, `mknodat`, `fchmod`, `fntimes`, `fchflags`, `fsetxattr`). `ceph_snap_get_btime_fsp()` reads `ceph.snap.btime`; `ceph_snap_enum_snapdir()` enumerates `.snap`; `ceph_snap_gmt_convert()` maps a time-warped path to a concrete snapshot path.

## Control Flow
Enumeration begins in `ceph_snap_get_shadow_copy_data()`, chooses either the directory's own snapshot namespace or the parent namespace for files, opens it with Samba directory helpers, checks `SEC_DIR_LIST`, and optionally formats labels from Ceph btime. Time-warped read operations detect nonzero `smb_filename->twrp`, convert the user path by searching matching snapshot btimes, and dispatch the converted path to the next VFS module. Mutating calls fail under snapshots with `EROFS`, while source snapshot renames fail with `EXDEV`.

## State And Persistence
There is no durable private state. Snapshot identity is derived on demand from CephFS directory entries and the `ceph.snap.btime` xattr. The only configuration is `ceph:snapdir`. Labels have one-second resolution, so same-second snapshots can collide.

## Dependencies And Integration Points
The module depends on Samba VFS dispatch, `struct smb_filename`, pathref helpers, `OpenDir()`/`ReadDirName()`, access checks, shadow-copy structures, and CephFS' virtual btime xattr. It intentionally marks `getxattrat_send/recv` as not implemented.

## Risks
Large snapshot directories make conversion and enumeration expensive. Old CephFS versions without `ceph.snap.btime` cannot work with this module. Path conversion temporarily swaps `base_name` values, so errno and lifetimes are delicate. Parent fallback follows Ceph inherited snapshot semantics and can surprise tests. Timestamp collisions are explicitly possible.

## Test Signals
Test Previous Versions enumeration, label formatting, `.snap` permission failures, custom snapdir, file and directory `@GMT` open/stat/realpath, inherited child lookup, write operations returning `EROFS`, snapshot rename returning `EXDEV`, malformed or absent btime xattrs, and same-second snapshots.
