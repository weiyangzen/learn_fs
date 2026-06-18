# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.c

## Purpose

`xfs_types.c` implements runtime validators for XFS scalar address and count types, including filesystem blocks, extents, inodes, realtime blocks, inode counts, directory/attribute block offsets, and file offsets.

## Main Content

- Validates AG block numbers:
  - Must be within the AG.
  - Must not point at static AG metadata through the AGFL block.
- Validates filesystem block numbers and extents:
  - Must map to an existing AG.
  - Must not overflow.
  - Must not cross AG boundaries.
  - Must not point at static AG metadata.
- Validates inode numbers:
  - AG number must exist.
  - AG inode encoding must round-trip.
  - AG inode must be within per-AG inode range.
- Identifies superblock/internal inode numbers: realtime bitmap, realtime summary, and quota inodes.
- Validates directory inode targets by rejecting internal inodes.
- Validates realtime block numbers and extents:
  - For rtgroups, checks RT group number, group extent count, first RT superblock extent exclusion, and group boundary crossing.
  - For non-rtgroups, checks against `sb_rblocks`.
- Computes valid inode count range by walking per-AG state.
- Validates inode count, directory/attribute block offsets, file offsets, and file offset ranges.

## Key Interfaces and Invariants

- Extent validators reject arithmetic overflow by checking `start + len <= start`.
- Data device extents cannot cross allocation group boundaries.
- RT group extents cannot cross realtime group boundaries.
- RT superblock reservation in group zero is not allocatable.
- Directory entries cannot point to internal superblock/quota/realtime metadata inodes.
- Minimum inode count assumes root, rtbitmap, and rtsum occupy the first inode chunk.

## Dependencies

Depends on mount geometry, per-AG iteration, AG inode range helpers, realtime group helpers, realtime block conversions, quota inode predicates, and format macros.
