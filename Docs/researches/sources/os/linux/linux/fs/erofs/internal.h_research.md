# File Research: sources/os/linux/linux/fs/erofs/internal.h

Defines EROFS in-memory state, mount options, mapping structures, feature helpers, and internal function prototypes.

Key behavior:
- Provides logging macros and debug BUG behavior.
- Defines EROFS scalar types for nid, offsets, and block numbers.
- Defines device info, mount options, device table context, LZ4 state, fscache/domain state, xattr prefix state, superblock private state, and inode private state.
- Defines mount flags for user xattrs, ACLs, DAX, direct I/O, and inode sharing.
- Provides mode helpers for file-backed and fscache mounts.
- Defines metadata buffer state and block/offset conversion helpers.
- Generates feature-test helpers for compat and incompat superblock bits.
- Defines metabox inode-number conversion and inode metadata location helpers.
- Defines map flags for mapped extents, inline metadata, partial mappings, fragment data, and full encoded-data coverage.
- Declares all major EROFS VFS operation tables, mapping helpers, sysfs helpers, decompression helpers, fscache/fileio helpers, and inode-sharing helpers.
- `erofs_get_aops()` selects compressed, fscache, file-backed, or standard address-space operations.

Important interactions:
- Central private header used by all EROFS implementation files.
- Compile-time feature stubs keep call sites simple when optional features are disabled.
