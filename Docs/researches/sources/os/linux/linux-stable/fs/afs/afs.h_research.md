# File Research: sources/os/linux/linux-stable/fs/afs/afs.h

This header defines common public AFS protocol types, limits, status records, callback records, volume records, and XDR helper structures.

Major definitions:
- Cell, volume, server, filename, pathname, and opaque-field length limits.
- VL and probe lifespan constants.
- Core typedefs for volume IDs, vnode IDs, and data versions.
- Volume type enum for read-write, read-only, and backup volumes.
- File type enum for file, directory, symlink, and invalid.
- Lock type enum and lock wait timeout.
- `struct afs_fid`, combining volume ID, vnode ID, high vnode bits, and unique generation.
- Callback type, callback promise, and callback-break records.
- AFS UUID layout.

Status and metadata:
- `struct afs_file_status` carries size, data version, client/server mtimes, author/owner/group, caller and anonymous access masks, Unix mode, file type, nlink, lock count, and abort status.
- `struct afs_status_cb` combines status with callback data and flags indicating which parts were returned.
- `struct afs_volsync` and `struct afs_volume_status` model volume-level synchronization and quota/status data.

Access model:
- Defines AFS ACL permission bits for read, write, insert, lookup, delete, lock, administer, and user-defined A-H permissions.
- Defines status-change mask bits for mtime, owner, group, mode, and segment size.

Wire/XDR structures:
- `AFS_BLOCK_SIZE` is 1024.
- `struct afs_uuid__xdr` represents UUID fields expanded into big-endian XDR words.
