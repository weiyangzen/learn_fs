# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_cksum.h

## Role in the repository

`xfs_cksum.h` provides inline CRC32c checksum helpers for XFS metadata buffers that contain an embedded checksum field. Btree checksum helpers in `xfs_btree.c` ultimately rely on these buffer checksum primitives.

## Checksum algorithm

The checksum seed is `XFS_CRC_SEED`, defined as all ones in a 32-bit value.

`xfs_start_cksum_safe` verifies a buffer without modifying it. It computes CRC32c in three pieces:
- Bytes before the checksum field.
- A zero value in place of the checksum field.
- Bytes after the checksum field.

This allows verification while preserving the buffer contents.

`xfs_start_cksum_update` is the faster update path. It requires exclusive buffer access, writes zero into the checksum field, and computes CRC32c over the whole buffer in one pass.

`xfs_end_cksum` converts the intermediate CRC into on-disk format by complementing and storing it little-endian. The comment notes that CRC32c computation uses little-endian format even on big-endian machines, so byte swapping is required for consistent disk format.

## Public helpers

`xfs_update_cksum` updates a buffer in place:
- Zero checksum field.
- Compute CRC32c.
- Store the finalized little-endian checksum.

`xfs_verify_cksum` verifies a buffer:
- Compute the safe CRC with a logical zero checksum field.
- Compare the embedded little-endian checksum with the finalized expected value.

## Important invariants

- Update callers must have exclusive access because the checksum field is temporarily modified.
- Verification callers do not modify the buffer.
- The checksum field offset is supplied by the caller, which lets the same helpers serve btree blocks and other metadata formats with different checksum locations.
