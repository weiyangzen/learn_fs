# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_err.et.in

## Purpose
`ext2_err.et.in` is the `com_err` error-table template for the ext2fs library. Build tooling substitutes `@E2FSPROGS_VERSION@` and generates the library error constants and human-readable messages used throughout `lib/ext2fs`.

## Content Summary
The file declares `error_table ext2` and then a linear list of `ec` entries from `EXT2_ET_BASE` through `EXT2_ET_EXTERNAL_JOURNAL_NOSUPP`.

The errors cover:
- Library and object magic-number validation failures for `ext2_filsys`, bitmaps, inode scans, directory block lists, extent handles, EA handles, and IO managers.
- Filesystem metadata corruption: bad superblocks, bad group descriptors, directory corruption, invalid inode/block numbers, bad inode tables, checksum mismatches.
- IO failures: short reads/writes, descriptor reads/writes, inode/block bitmap IO, inode table IO, llseek failures.
- Allocation and mutation failures: no memory, block/inode allocation failure, directory no-space, file-too-big, unsupported operations.
- Journal handling: missing/unsupported journals, corrupt journal superblock, external journal limitations.
- Directory hashing and htree support.
- Extent operations: bad headers/index/leaves, no next/previous/up/down, insertion/split failures, invalid lengths, cycles.
- 64-bit and large filesystem limits: unsupported 64-bit IO channels, legacy bitmap limitations, descriptor size errors.
- MMP errors: invalid magic, active device, fsck active, sequence changes, checksum invalid.
- Metadata checksum failures for inodes, bitmaps, directories, extents, xattr blocks, superblock, MMP.
- Extended attribute and inline-data errors: malformed names/value sizes/offsets, bad EA hash/header, missing features, no inline data/space/block, bad EA inode.
- Undo-file, CRC, filesystem, and internal structure corruption errors.

## Integration
Generated output is included by `ext2fs.h` as `ext2_err.h`, and most `.c` files return these symbolic errcodes. This file is therefore part of the public ABI surface: the order of entries affects generated numeric values.

## Risks and Notes
- Reordering entries can break consumers that compare numeric errcodes.
- New library errors should be appended, not inserted, unless ABI compatibility is intentionally handled.
- Messages are user-visible through `com_err`, e2fsck, debugfs, and other e2fsprogs tools.
