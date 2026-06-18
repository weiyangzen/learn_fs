# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/dat.h

Defines `ext2srv`'s shared data model: ext2 on-disk structures, server state, constants, and error numbers.

Key contents:
- Ext2 superblock, group descriptor, inode, and directory entry structures.
- Ext2 constants for magic, block sizes, root inode, valid state, inode block pointers, and file type bits.
- `Iobuf`, the block cache entry used by `iobuf.c`.
- `Xfs`, the open ext2 device/filesystem state, including computed block size, group layout, inode layout, and cache-related metadata.
- `Xfile`, the per-Plan-9-fid state attached through lib9p `Fid->aux`.
- `Ext2`, a typed wrapper around cached superblock, group descriptor, or bitmap blocks.

Important relationships:
- `Xfile` stores `inbr`, `pinbr`, inode block address, and inode offset; most ext2 operations use this instead of holding an inode object.
- `DESC_ADDR` and `DESC_OFFSET` map group numbers to descriptor blocks and descriptor slots.
- Error enum indexes are paired with strings in `errstr.h`.

Risks and invariants:
- The on-disk structures are defined with native C fields and assume the Plan 9 build target's layout matches the expected ext2 little-endian representation.
- Only classic ext2 fields are modeled; newer ext2/ext3/ext4 extensions are outside this server's scope.
