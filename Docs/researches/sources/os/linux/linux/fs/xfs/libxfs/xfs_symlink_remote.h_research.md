# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.h

## Purpose

`xfs_symlink_remote.h` declares the symlink encoding, verification, read, write, conversion, and truncation helpers implemented for XFS remote symlink targets.

## Main Content

- Declares symlink block count calculation.
- Declares CRC symlink header set/check helpers.
- Declares local-to-remote conversion helper.
- Declares shortform in-memory verifier.
- Declares remote symlink read/write helpers.
- Declares remote symlink truncation helper.

## Key Interfaces and Invariants

- `xfs_symlink_hdr_set` returns header size so callers can advance to payload.
- `xfs_symlink_write_target` accepts owner inode, target path, target length, allocated block count, and reservation block count.
- `xfs_symlink_shortform_verify` checks in-memory consistency, not full on-disk buffer format.

## Dependencies

Relies on XFS mount, inode, ifork, transaction, buffer, block, and fail-address types declared by surrounding headers.
