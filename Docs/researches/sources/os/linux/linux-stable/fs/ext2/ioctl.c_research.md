# File Research: sources/os/linux/linux-stable/fs/ext2/ioctl.c

## Summary
Implements ext2 file attribute get/set and legacy ext2 ioctl handling for inode generation and reservation-window size.

## Main Responsibilities
- Exposes user-visible ext2 inode flags through `fileattr`.
- Updates user-modifiable inode flags and maps them to VFS inode flags.
- Handles get/set inode generation ioctls.
- Handles get/set reservation window size ioctls.
- Provides compat ioctl translation for 32-bit generation ioctls.

## Key APIs
- `ext2_fileattr_get()`.
- `ext2_fileattr_set()`.
- `ext2_ioctl()`.
- `ext2_compat_ioctl()`.

## Important Behavior
`ext2_fileattr_set()` rejects fsx-style attributes, rejects quota files, updates only `EXT2_FL_USER_MODIFIABLE`, refreshes VFS flags, updates ctime, and dirties the inode.

`EXT2_IOC_SETVERSION` requires ownership/capability and a writable mount. Reservation size ioctls require regular files and the reservation mount option; setting size lazily creates block allocation info under `truncate_mutex` and clamps to `EXT2_MAX_RESERVE_BLOCKS`.

## Risks
Reservation size locking is noted as uncertain in a comment; practical protection is via `truncate_mutex`. The compat path only translates version ioctls, not reservation-size ioctls.
