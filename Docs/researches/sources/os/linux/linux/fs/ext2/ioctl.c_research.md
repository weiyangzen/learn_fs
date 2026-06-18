# File Research: sources/os/linux/linux/fs/ext2/ioctl.c

Read status: complete, 159 lines.

This file implements ext2 ioctl and file attribute operations.

Key responsibilities:
- Gets and sets user-visible ext2 inode flags through `ext2_fileattr_get()` and `ext2_fileattr_set()`.
- Handles `EXT2_IOC_GETVERSION` and `EXT2_IOC_SETVERSION` for inode generation.
- Handles `EXT2_IOC_GETRSVSZ` and `EXT2_IOC_SETRSVSZ` for per-regular-file reservation window size.
- Provides compat ioctl translation for 32-bit generation ioctls.

Behavior:
- Fileattr set rejects fsx-style attributes and quota files.
- Fileattr set masks updates to `EXT2_FL_USER_MODIFIABLE`, then applies VFS inode flags through `ext2_set_inode_flags()`.
- Setting inode generation requires owner/capability check and a writable mount.
- Reservation-size ioctls require reservation mount option, regular file type, and owner/capability for setting.
- Reservation size is capped at `EXT2_MAX_RESERVE_BLOCKS`.
- If needed, setting reservation size lazily allocates `i_block_alloc_info` under `truncate_mutex`.

Safety and permissions:
- Uses `inode_owner_or_capable()` for privileged mutation.
- Uses `mnt_want_write_file()`/`mnt_drop_write_file()` around mutating ioctls.
- User pointer access uses `get_user()`/`put_user()`.
- Quota files are protected from user flag mutation.

Research notes:
- This is a small control-plane file for legacy ext2 ioctls and modern fileattr hooks.
- Reservation-size ioctls connect user-visible tuning to allocator state in `balloc.c`.
