# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/csum.c

Implements ext2/ext4 metadata checksum support. It covers checksum seed initialization, MMP, superblock, extended attribute blocks, directory blocks, htree index blocks, extent blocks, inode/block bitmaps, inodes, group descriptors, and GDT checksum updates.

Major API groups:
- Seed/type: `ext2fs_init_csum_seed`, `ext2fs_verify_csum_type`.
- MMP: verify/set checksum over `struct mmp_struct`.
- Superblock: verify/set checksum over the superblock up to `s_checksum`.
- EA block: verify/set checksum using block number and UUID or checksum seed.
- Directory tails: locate/initialize dirent checksum tail and htree dx tail.
- Directory block checksum: verify/set normal dirent tail or htree dx checksum.
- Extent block checksum: verify/set extent tree tail checksum.
- Bitmap checksum: verify/set inode and block bitmap checksums in group descriptors.
- Inode checksum: verify/set inode checksum with optional high checksum field.
- Group descriptor checksum: compute, verify, set old crc16 or metadata_csum crc32c.
- GDT update: `ext2fs_set_gdt_csum` updates uninit flags, itable unused watermark, and descriptor checksums.

Important behavior:
- Metadata checksums use `fs->csum_seed`; old group descriptor checksums use CRC16 seeded by UUID and group.
- Directory checksum code distinguishes normal directory tails from htree dx tails.
- Inode checksum verification treats an all-zero base inode as valid despite mismatch.
- Big-endian descriptor checksums temporarily swab descriptor fields back to little-endian form for checksum calculation.
- `EXT2_FLAG_IGNORE_CSUM_ERRORS` suppresses some directory checksum failures.

Dependencies: CRC16, CRC32C, descriptor accessors, inode read, directory structures, extents, feature flags.

Implementation notes:
- Many setters are no-ops when the relevant checksum feature is disabled.
- Group descriptor checksum calculation intentionally zeros the checksum field during calculation.
- `ext2fs_set_gdt_csum` requires an inode bitmap and marks the superblock dirty if flags, unused counts, or checksums change.
- The file contains debug/unit-test code under `DEBUG`.
