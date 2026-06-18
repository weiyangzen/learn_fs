# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/link.c

## Purpose
Tracks on-disk link counts and counted directory-entry references so later fsck passes can detect and repair link-count mismatches.

## Main Elements
- Globals:
  - `nlink1map`: one-bit map for non-directory dinodes whose on-disk `i_nlink` is exactly 1.
  - `clink1map`: one-bit map for non-directory dinodes with exactly one counted reference.
- `link1_set()`: sets or clears one-bit map entries.
- `set_di_nlink()`: records an inode’s on-disk link count in `dirtree`, `nlink1map`, or `inodetree`.
- `incr_link_count()`: increments counted references for directories, known inodes, one-link-map entries, or promotes a one-link inode into the full inode tree when a second reference is found.
- `decr_link_count()`: decrements counted references for directory/inode tree entries or clears the counted-one-link bit.

## Dependencies And Integration
Uses directory tracking from `dirtree_find()`, inode tracking from `inode_hash.c`, bitmap helpers from `util.h`, and `fsck_load_inode()` / `fsck_inode_put()` when validating promoted hard links. Called by directory traversal, lost+found repair, duplicate cleanup, and pass4 link reconciliation.

## Behavioral Notes
`incr_link_count()` validates formal inode numbers and can return `INCR_LINK_CHECK_ORIG` when a second reference to a previously one-link non-directory inode requires checking the first reference. The one-bit maps avoid allocating full tree nodes for the common one-link case.
