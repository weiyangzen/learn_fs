# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.c

## Purpose

`xfs_symlink_remote.c` implements XFS symlink target encoding, verification, reading, writing, local-to-remote conversion, and remote block truncation. It handles both legacy unheadered symlink blocks and CRC-protected symlink blocks with headers.

## Main Content

- Computes how many filesystem blocks are needed for a symlink target after accounting for per-block headers.
- Initializes CRC symlink headers with magic, target offset, byte count, metadata UUID, owner inode, and disk address.
- Validates symlink header owner, offset, and byte count.
- Verifies symlink buffers:
  - Magic.
  - Metadata UUID.
  - Disk address.
  - Bounds against `XFS_SYMLINK_MAXLEN`.
  - Owner.
  - LSN.
  - CRC.
- Defines `xfs_symlink_buf_ops`.
- Converts inline/local symlink data to a remote block during fork format conversion.
- Verifies in-memory shortform symlink targets:
  - Nonzero length.
  - Nonnegative and within max length.
  - No interior NUL.
  - NUL terminator present.
- Reads remote symlink extents into a caller buffer, validating headers for CRC filesystems and marking symlink metadata sick on corruption.
- Writes symlink targets inline when they fit in the inode data fork or allocates/writes remote metadata blocks otherwise.
- Invalidates and unmaps remote symlink blocks during truncation.

## Key Interfaces and Invariants

- CRC symlink blocks include a header, reducing payload capacity per block.
- Legacy non-CRC symlink buffers have no verifier work.
- Header verification is split: buffer verifier checks block identity and bounds; read path checks caller-expected owner/offset/length.
- Remote read expects the bmap to cover the entire target and NUL-terminates the caller buffer.
- Remote truncate must both invalidate buffers and unmap extents; failure to unmap marks symlink metadata sick.
- Inline symlink write switches the data fork to `XFS_DINODE_FMT_LOCAL` and logs data/core.

## Dependencies

Depends on inode fork management, bmap read/write/unmap, transactions, buffer verifiers and CRC helpers, log item LSNs, mount feature predicates, and health marking.
