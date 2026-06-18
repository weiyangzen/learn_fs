# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unix.go

## Purpose
Implements `BasicFilesystem` extended attribute read/write support on Unix-like platforms with xattr APIs.

## Important APIs, Types, and Functions
`GetXattr`, `SetXattr`, `xattrBufPool`, `getXattr`, and `compact`. `GetXattr` applies `XattrFilter` permission, max-entry, and max-total limits. `SetXattr` reconciles current and desired attributes by removing absent entries and setting changed values.

## Control Flow
`GetXattr` roots the path, lists names, filters names, reads values with `Lgetxattr`, handles BSD `ENOATTR`, applies size limits, and returns `protocol.Xattr` values. `getXattr` uses a pooled buffer, resizes on `ERANGE`, and returns either the buffer slice or a compact copy. `SetXattr` indexes desired/current xattrs, roots the path, removes no-longer-present xattrs, then sets new or changed values.

## State and Persistence Behavior
Reads and mutates filesystem xattrs on symlink paths using l* APIs. Size filters affect what gets synchronized or deleted.

## Dependencies and Integration Points
Depends on platform `listXattr`, `protocol.Xattr`, `x/sys/unix`, and `Filesystem.PlatformData`.

## Risks
Current xattrs are fetched through the same filter, so unpermitted attributes are intentionally untouched. Concurrent changes can cause missing-attribute races. Large xattr values can increase memory retention if returned from pooled buffers.

## Test Signals
`TestXattr` verifies set, read, removal, mutation, addition, sorting, and unsupported-platform skips.
