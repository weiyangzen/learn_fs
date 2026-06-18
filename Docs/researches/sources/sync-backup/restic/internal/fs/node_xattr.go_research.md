# sources/sync-backup/restic/internal/fs/node_xattr.go

Purpose: POSIX-like xattr backup and restore implementation for Darwin, FreeBSD, NetBSD, Linux, and Solaris.

Important APIs: `getxattr`, `listxattr`, `isListxattrPermissionError`, `setxattr`, `removexattr`, `handleXattrErr`, `nodeRestoreExtendedAttributes`, and `nodeFillExtendedAttributes`.

Control flow and state: Backup lists xattr names, optionally ignores permission errors, reads each value, warns and skips individual unreadable attributes, and appends them to the node. Restore sets expected xattrs that match the selection filter, lists current xattrs, and removes unexpected selected ones.

Dependencies and integration: Uses `github.com/pkg/xattr` and `data.ExtendedAttribute`. Called by generic node conversion/restore.

Risks: `handleXattrErr` treats unsupported/ENOATTR as nil, which can hide unsupported metadata. Restore removal is filter-sensitive, so excluded xattrs are left untouched. `warnf` must be non-nil when individual reads fail.

Test signals: `node_xattr_test.go` verifies permission-error detection; `node_xattr_all_test.go` verifies overwrite/removal and selection filters.
