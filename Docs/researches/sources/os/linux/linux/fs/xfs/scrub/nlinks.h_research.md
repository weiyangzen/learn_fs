# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks.h

## Role
Defines the data structures shared by live nlink scrub and repair.

## Main Structures
- `struct xchk_nlink_ctrs` holds the scrub context, sparse shadow link-count array, mutex, collection and comparison iscans, dirent hook, orphanage adoption state, and reusable name buffer.
- `struct xchk_nlink` records observed `parents`, `backrefs`, `children`, and state flags for one inode.

## Flags
- `XCHK_NLINK_WRITTEN` marks initialized shadow records.
- `XCHK_NLINK_COMPARE_SCANNED` marks records already compared.
- `XREP_NLINK_DIRTY` marks records already repaired.

## Link Total
- `xchk_nlink_total` computes the expected `i_nlink` from observed parent links plus child-directory links.
- Linked directories get one extra count for `.`.
