# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_cksum.h

## Purpose

`xfs_cksum.h` provides small inline CRC32c helper routines for XFS metadata buffers whose checksum field lives inside the buffer being checksummed.

## Main Helpers

`xfs_start_cksum_safe` computes an intermediate checksum without modifying the buffer. It calculates CRC32c over the bytes before the checksum field, feeds four zero bytes for the checksum field, and then continues over the rest of the buffer.

`xfs_start_cksum_update` is the faster mutable path. It zeroes the checksum field in place and computes CRC32c over the whole buffer. Callers must have exclusive access.

`xfs_end_cksum` converts the intermediate CRC to on-disk little-endian inverted format.

`xfs_update_cksum` zeroes the field, computes the checksum, finalizes it, and writes it back to the buffer.

`xfs_verify_cksum` computes the safe checksum and compares it with the stored finalized value.

## Constants

`XFS_CRC_SEED` is the CRC32c seed value, defined as all bits set.

## Integration Points

These helpers are used by XFS metadata buffer checksum wrappers such as btree block CRC calculation and verification. They rely on the kernel `crc32c` implementation and endian conversion helpers.

## Important Invariants

- Safe verification must not mutate the buffer.
- Update mode temporarily mutates the checksum field and therefore requires exclusive access.
- XFS stores CRC32c results in little-endian inverted form for consistent on-disk representation.
- The checksum offset must identify a 32-bit checksum field fully contained in the buffer.
