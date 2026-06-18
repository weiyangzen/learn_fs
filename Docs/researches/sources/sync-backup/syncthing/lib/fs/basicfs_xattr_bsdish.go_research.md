# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_bsdish.go

## Purpose
Lists extended attributes on FreeBSD and NetBSD while preserving namespace information missing from Go's generic API.

## Important APIs, Types, and Functions
Defines `namespaces`, `namespacePrefixes`, `listXattr`, `unixLlistxattr`, and `initxattrdest`.

## Control Flow
`listXattr` iterates user and system namespaces, reads length-prefixed extattr names, prefixes them with `user.` or `system.`, handles buffer growth, ignores EPERM for non-user namespaces, sorts names, and returns them.

## State and Persistence Behavior
Read-only metadata query. No xattrs are mutated here.

## Dependencies and Integration Points
Used by `basicfs_xattr_unix.go` on FreeBSD/NetBSD. Calls `unix.ExtattrListLink` directly to retain namespace IDs.

## Risks
Parsing length-prefixed buffers must guard corrupt lengths; it does. Namespace prefix array indexing is tied to unix constants. Permission-denied system namespace is silently ignored.

## Test Signals
Indirectly covered by `TestXattr` when run on supported BSD platforms.
