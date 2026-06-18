# File Research: sources/local-fs/xfsprogs/db/symlink.c

Defines field decoding for CRC-enabled remote symlink blocks.

Key responsibilities:
- Computes symlink block display size and target-data count.
- Defines the `symlink_crc` header field table: magic, offset, bytes, crc, uuid, owner, block number, lsn, and data.
- Validates symlink magic before reporting size/count.

Important behavior:
- `symlink_count` bounds displayed data to the filesystem block size if `sl_bytes` is too large.
- `symlink_size` returns header plus target byte count only for valid symlink magic.

Dependencies:
- Uses `xfs_dsymlink_hdr`, global `mp`, field/type helpers, and CRC field types.

Notable risks:
- Comment notes no support for multiple contiguous block symlinks in this display path.
