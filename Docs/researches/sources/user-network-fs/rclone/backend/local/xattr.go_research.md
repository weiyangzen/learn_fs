
# sources/user-network-fs/rclone/backend/local/xattr.go

## Purpose
Implements user metadata storage through extended attributes on platforms supported by `pkg/xattr`.

## Important APIs, Types, And Control Flow
Defines `xattrPrefix = "user."` and `xattrSupported = xattr.XATTR_SUPPORTED`. `xattrIsNotSupported` detects ENOTSUP, ENOATTR, and EINVAL, disables future xattr operations atomically, and logs once. `getXattr` lists and reads attributes with follow/no-follow variants, lowercases names, filters non-`user.` and backend-owned system metadata keys, and returns user metadata. `setXattr` writes non-system metadata as `user.<key>`.

## State And Persistence
Persists user metadata as filesystem xattrs. Runtime state includes the `Fs.xattrSupported` atomic flag that can disable xattr use after unsupported errors.

## Dependencies And Integration Points
Used by local object and directory metadata read/write paths. Integrates with `github.com/pkg/xattr`, local symlink-following options, and `systemMetadataInfo`.

## Risks And Test Signals
Risks include namespace portability, lowercasing key names, symlink xattr support differences, partial writes, and dynamic disabling after one unsupported error. Metadata tests cover read/write and symlink limitations.
