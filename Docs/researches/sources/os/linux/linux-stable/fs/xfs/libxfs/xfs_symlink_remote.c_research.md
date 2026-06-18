# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.c

## Purpose

Implements remote symlink block formatting, verification, reading, writing, conversion from local to remote format, shortform verification, and truncation.

## Main Responsibilities

- Computes required remote symlink blocks with `xfs_symlink_blocks`.
- Creates CRC symlink headers through `xfs_symlink_hdr_set`.
- Validates symlink headers through `xfs_symlink_hdr_ok`.
- Defines `xfs_symlink_buf_ops` for remote symlink buffer verification.
- Converts inline symlink data into a remote symlink block.
- Verifies in-memory shortform symlink payloads.
- Reads remote symlink data across mapped blocks.
- Writes symlink targets either inline or into remote blocks.
- Invalidates and unmaps remote symlink blocks during truncate/removal.

## Important Invariants

- CRC-enabled filesystems store `struct xfs_dsymlink_hdr` at the start of each remote symlink buffer.
- Header fields must match:
  - symlink owner inode
  - byte offset
  - byte count
  - filesystem metadata UUID
  - buffer disk address
- Remote symlink header offset plus bytes must remain below `XFS_SYMLINK_MAXLEN`.
- Shortform symlink data must be nonempty, length-bounded, free of embedded nulls, and null-terminated in memory.
- Non-CRC filesystems do not verify or write symlink headers.

## Dependencies

- Uses bmap read/write/unmap APIs for remote block mapping.
- Uses transaction buffer logging and invalidation.
- Marks inode symlink sickness on metadata corruption.

## Research Notes

This file protects symlink target integrity for CRC filesystems by tying each remote block to owner, location, offset, and length. The split between buffer verifier checks and caller-level owner/offset checks is intentional.
