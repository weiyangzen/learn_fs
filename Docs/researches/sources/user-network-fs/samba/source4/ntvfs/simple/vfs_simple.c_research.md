# sources/user-network-fs/samba/source4/ntvfs/simple/vfs_simple.c

Purpose: `vfs_simple.c` implements Samba4's `simple` NTVFS disk backend. It is a minimal file server backend that maps a small subset of SMB operations directly to POSIX file calls and intentionally omits much of the correct CIFS/NTFS compatibility behavior.

Important APIs, types, and functions: Key functions include `svfs_connect`, `find_fd`, `svfs_unlink`, `svfs_chkpath`, `svfs_map_fileinfo`, `svfs_qpathinfo`, `svfs_qfileinfo`, `svfs_open`, `svfs_mkdir`, `svfs_rmdir`, `svfs_rename`, `svfs_read`, `svfs_write`, `svfs_flush`, `svfs_close`, `svfs_setfileinfo`, `svfs_fsinfo`, search first/next/close handlers, and `ntvfs_simple_init`.

Control flow: Tree connect verifies the configured share path and records it in `svfs_private`. Open maps generic create dispositions to `open` flags, optionally creates directories, creates an NTVFS handle, and links an `svfs_file`. Query operations stat paths/fds and fill generic fileinfo. Search first snapshots a directory into `svfs_dir`, emits entries through the callback, and either stores or frees search state depending on client flags. Close fsync/close paths operate directly on tracked fds.

State and persistence behavior: Runtime state is an open-file linked list and search linked list under the connection. Persistent effects are direct filesystem changes: create, mkdir, unlink, rename, write, truncate, fsync, and timestamp updates. It does not persist Samba-specific xattrs, locks, ACLs, or oplocks.

Dependencies and integration points: It integrates with the NTVFS operation table, generic NTVFS mapping helpers for unsupported levels, Samba share options, statvfs helpers, POSIX file APIs, and `svfs_util.c`.

Risks: It ignores wildcards for unlink/rename, does not implement byte-range locks, returns placeholder errors such as `NT_STATUS_FOOBAR`, has weak metadata mapping, and defaults read-only checks through share options. It should not be treated as a production NTFS-compatible backend.

Test signals: Tests should exercise supported generic open/read/write/query/search/fsinfo flows and verify unsupported operations return stable errors. Regression coverage should include read-only shares, directory opens, search resume flags, flush-all behavior, truncate/time set, and handle invalidation after close.
