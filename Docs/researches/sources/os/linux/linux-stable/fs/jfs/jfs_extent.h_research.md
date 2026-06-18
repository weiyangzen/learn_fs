# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_extent.h

This header declares the JFS extent allocation API and the inode-based allocation hint macro.

Key responsibilities:
- Defines `INOHINT(ip)`, which uses the inode extent descriptor as a block allocation hint.
- Declares `extAlloc()` for allocating file extents.
- Declares `extHint()` for deriving allocation hints from nearby file offsets.
- Declares `extRecord()` for changing an extent from not-recorded to recorded.

Important interactions:
- Depends on `JFS_IP(ip)->ixpxd` and extent descriptor helpers such as `addressPXD()` and `lengthPXD()`.
- Used by file/block mapping code that needs to allocate or update regular-file xtree records.

Notable invariants and risks:
- `INOHINT()` assumes the inode extent descriptor has a valid address and length.
- The API exposes `xad_t` directly, so callers must preserve correct offset, length, address, and `XAD_NOTRECORDED` semantics.

Research notes:
- This is a small public surface for the extent allocator implemented in `jfs_extent.c`.
