# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.h

## Scope

This header defines the public kernel interface for the VFS-backed exclave filesystem bridge.

## APIs And Constants

- Defines packed `exclave_fs_dirent_t` with attrlist return fields, object type, file id, name location/length, and data length.
- Defines `EXCLAVE_FS_BASEDIR_ROOT_ID`.
- Defines sync operations: barrier, full fsync, and UBC fsync.
- Defines register/list entitlement strings.
- Declares lifecycle, registration, root/open/create/close/read/write/remove/sync/readdir/getsize/sealstate APIs.
- Declares `vfs_exclave_fs_query_volume_group()`.

## Dependencies And Role

The header includes kernel type definitions and assumes vnode, UUID string, and bool types are available from included kernel context.

## Risks And Invariants

- `exclave_fs_dirent_t` is packed and must match the byte layout produced by `VNOP_GETATTRLISTBULK()` consumers.
- API callers must treat file ids as opaque, especially for graft-backed base directories.
- The header exposes entitlement names but enforcement is performed by call sites outside this header.
