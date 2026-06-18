# sources/user-network-fs/samba/source3/modules/vfs_posix_eadb.c

## Purpose
`vfs_posix_eadb.c` implements POSIX extended attributes using a TDB database instead of filesystem-native xattrs. It is for environments where Samba must preserve POSIX EA semantics but the backing filesystem cannot, or should not, store them directly.

## Important APIs, Types, And Functions
- `posix_eadb_getattr`, `posix_eadb_setattr`, `posix_eadb_listattr`, and `posix_eadb_removeattr` wrap raw TDB xattr helpers from `ntvfs/posix/posix_eadb.h`.
- File-facing hooks `posix_eadb_fgetxattr`, `posix_eadb_fsetxattr`, `posix_eadb_flistxattr`, and `posix_eadb_fremovexattr` fetch the per-handle `struct tdb_wrap` via `SMB_VFS_HANDLE_GET_DATA`.
- `posix_eadb_init()` opens the database from the `posix:eadb` share parameter as root with `tdb_wrap_open`.
- `posix_eadb_unlink_internal()` and `posix_eadb_rmdir_internal()` delete EA records transactionally when the backing file or directory is removed.
- `posix_eadb_connect()` opens the DB and toggles `ea support` based on availability.

## Control Flow
On connect, the module delegates to the next VFS connect, resolves the service number, opens the configured EA database, and stores the `tdb_wrap` as VFS handle data. Xattr hooks translate the `files_struct` name/fd to raw DB helper calls. On unlink, the module builds a full path, stats it, starts a TDB transaction for last-link deletion, removes the EA record, delegates the unlink, then commits or cancels the transaction. Directory removal follows a similar record-delete plus `AT_REMOVEDIR` unlink flow.

## State And Persistence
Persistent EA data lives in the configured TDB file. The VFS handle stores a `tdb_wrap` pointer with a destructor. The module modifies Samba service state by setting `ea support` true if DB initialization succeeds and false if it fails.

## Dependencies And Integration Points
It depends on TDB, Samba loadparm helpers, generated NDR xattr support, raw posix_eadb helpers, and VFS path construction/stat/unlink APIs. It integrates with Samba's f* xattr hooks, not path-based async xattr hooks, which are mapped to not-implemented stubs.

## Risks
- Correct cleanup depends on link count: EA records are only removed on unlink when `st_ex_nlink == 1`.
- Transaction handling is critical; failed unlink or failed TDB commit must not leave DB/filesystem state inconsistent.
- `posix:eadb` misconfiguration silently disables EA support for the service after logging.
- Full-path construction and POSIX path flags affect whether `STAT` or `LSTAT` is used before deletion.

## Test Signals
- Configure `posix:eadb`, set/list/get/remove xattrs through SMB, and verify persistence in the DB.
- Remove files with single and multiple hard links; EA records should survive until the last link disappears.
- Remove directories with EAs and verify records are deleted transactionally.
- Simulate missing or unwritable DB path and verify the share continues with `ea support = False`.
