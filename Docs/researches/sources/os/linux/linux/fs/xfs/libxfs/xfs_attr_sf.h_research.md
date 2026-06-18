# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose
Defines shortform extended attribute helper types and inline entry navigation/size routines for attributes packed inside the inode literal area.

## Main Interfaces
- `xfs_attr_sf_sort_t` describes sortable shortform entries for hash-ordered listing.
- `XFS_ATTR_SF_ENTSIZE_MAX` defines the maximum one-byte name/value length representable in shortform entries.
- `xfs_attr_sf_entsize_byname()` computes entry size from name and value lengths.
- `xfs_attr_sf_entsize()` computes entry size from an entry.
- `xfs_attr_sf_firstentry()`, `xfs_attr_sf_nextentry()`, and `xfs_attr_sf_endptr()` navigate the packed shortform buffer.

## Data Model
Shortform entries contain one-byte name and value lengths, namespace flags, and contiguous `nameval` storage. The total shortform buffer size is stored in the header as big-endian `totsize`; the end pointer helper converts it before pointer arithmetic.

## Integration Points
Used heavily by `xfs_attr_leaf.c` shortform add/remove/find/verify/convert code and by `xfs_attr.c` when estimating whether a new attr fork can start in shortform.

## Risks And Review Focus
- Pointer arithmetic assumes verified packed-entry bounds; callers must validate raw buffers before walking untrusted disk contents.
- One-byte length limits force conversion to leaf format for large names or values.
