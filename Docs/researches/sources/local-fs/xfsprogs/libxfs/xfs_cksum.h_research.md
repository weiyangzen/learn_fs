# File Research: sources/local-fs/xfsprogs/libxfs/xfs_cksum.h

## Purpose

`xfs_cksum.h` provides small inline CRC32c helpers for XFS metadata buffers. It supports both checksum verification without modifying a buffer and checksum generation by temporarily zeroing the checksum field.

## CRC Seed

`XFS_CRC_SEED` is defined as the bitwise inverse of zero as a 32-bit value. All helper calculations start from this seed.

## Safe Verification Path

`xfs_start_cksum_safe` computes the intermediate checksum for a buffer without modifying the buffer. It:

1. computes CRC32c from the beginning of the buffer up to the checksum field;
2. feeds a zero 32-bit value for the checksum field;
3. computes CRC32c over the remainder of the buffer.

This is used when verifying metadata because verification should not alter the buffer contents.

`xfs_verify_cksum` compares the stored little-endian checksum field to `xfs_end_cksum` of the safe intermediate CRC.

## Update Path

`xfs_start_cksum_update` is the faster generation path for callers with exclusive buffer access. It zeroes the checksum field in the buffer and calculates CRC32c over the whole buffer in one pass.

`xfs_update_cksum` computes the checksum with that update path and writes the final checksum back into the buffer.

## Finalization

`xfs_end_cksum` converts the intermediate CRC to the final ondisk format by complementing the little-endian value. The comment notes that CRC32c returns host-endian results but XFS stores the checksum consistently in little-endian format.

## Dependencies

This header depends on `crc32c`, endian helpers, and XFS integer typedefs. Btree CRC helpers in `xfs_btree.c` ultimately rely on this style of checksum logic through buffer checksum wrappers.
