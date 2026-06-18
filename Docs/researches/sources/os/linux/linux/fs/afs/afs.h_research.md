# File Research: sources/os/linux/linux/fs/afs/afs.h

Purpose: defines public/common AFS protocol types, constants, status records, access masks, callbacks, volume metadata, and XDR UUID layout.

Key contents:
- Name/path/cell/volume/server limits: `AFS_MAXCELLNAME`, `AFS_MAXVOLNAME`, `AFSNAMEMAX`, `AFSPATHMAX`, etc.
- Core typedefs: volume ID, vnode ID, data version.
- Enums for volume type, file type, and lock type.
- `struct afs_fid`: volume, vnode low/high, unique generation.
- Callback structs and callback break records.
- `struct afs_volume_info`, `struct afs_file_status`, `struct afs_status_cb`, `struct afs_volsync`, `struct afs_volume_status`.
- ACL access bit masks and file status change flags.
- `AFS_BLOCK_SIZE` and `struct afs_uuid__xdr`.

Implementation notes:
- `afs_status_cb` carries status/callback presence flags and inline per-file abort state.
- File status stores both client and server mtimes, access rights, mode, type, nlink, lock count, and abort code.
- Some historical callback fields are commented out, showing simplified in-kernel tracking.

Dependencies:
- Shared by FS, VL, callback, inode, and directory code.
