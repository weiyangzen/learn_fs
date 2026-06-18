# sources/user-network-fs/samba/source3/modules/vfs_xattr_tdb.c

## Purpose
`vfs_xattr_tdb.c` stores POSIX-style extended attributes in a Samba TDB database rather than on the underlying filesystem. It enables EA support on filesystems without native xattrs and can optionally pass `user.*` xattrs through to the backend filesystem.

## Important APIs, Types, and Functions
`struct xattr_tdb_config` stores the db handle and `ignore_user_xattr`. `xattr_tdb_init()` opens the configured TDB path, defaults to `state_path("xattr.tdb")`, and toggles `ea support`. Async getxattr support is implemented by `xattr_tdb_getxattrat_send/recv()` and callback `xattr_tdb_getxattrat_done()`. Synchronous fd hooks include `xattr_tdb_fgetxattr()`, `xattr_tdb_fsetxattr()`, `xattr_tdb_flistxattr()`, and `xattr_tdb_fremovexattr()`. `xattr_tdb_openat()` and `xattr_tdb_mkdirat()` clear stale attrs for newly created objects. `xattr_tdb_unlinkat()` removes all stored attrs when a removed object's final link or directory record goes away.

## Control Flow
Most operations lazily initialize config. If `ignore_user_xattr` is true and the xattr name starts with `user.`, operations delegate to the next VFS module. Otherwise the module obtains a file id from stat information and calls `xattr_tdb_*` library routines. On new file or directory creation, it removes all attrs for the new file id to avoid stale records from id reuse. On unlink, it stats before deletion, delegates unlink, and removes the DB record only when the object is removed or the last hard link is gone.

## State and Persistence
Persistent state is the TDB database containing xattr records keyed by Samba file id. The module stores one db handle per VFS handle. Native backend xattrs may also persist when `ignore_user_xattr` is enabled.

## Dependencies and Integration Points
It depends on dbwrap, `source3/lib/xattr_tdb.h`, Samba async VFS xattr APIs, file-id creation, pathref open helpers, and loadparm. It integrates with `ea support` by enabling it after successful DB init and disabling it on init failure.

## Risks
File-id reuse is mitigated on create/mkdir but remains sensitive to filesystems with unstable IDs. Mixed TDB and backend `user.*` listing can produce concatenated lists whose sizing/duplicates must be correct. In async getxattr passthrough, the local `smb_fname` variable is null in the delegation branch, which should be reviewed against `SMB_VFS_NEXT_GETXATTRAT_SEND` expectations. DB corruption or permission errors disable EA support.

## Test Signals
Tests should cover configured/default DB paths, init failure toggling `ea support`, get size-only/value/ERANGE, set flags, list with and without backend user xattrs, remove, create/mkdir stale cleanup, unlink hard-link semantics, symlink/POSIX path stat behavior, and async passthrough.
