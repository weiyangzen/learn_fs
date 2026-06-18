# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/extent.c

Read coverage: complete file read, 495 lines.

Purpose: verifies and optionally repairs OCFS2 extent trees hanging from inodes during fsck pass 1.

Behavior:
- `check_eb()` reads extent blocks without full validation, checks block number and filesystem generation, optionally invalidates or fixes them, then checks their embedded extent list.
- `check_el()` validates list depth, count, next-free record, record cpos ordering, hole policy, out-of-range blocks, and recursively descends interior records.
- `check_er()` checks individual records, delegates leaf-record validation, and clears invalid extent-block references when prompted.
- `o2fsck_check_extent_rec()` fixes unaligned physical block starts, truncates extents that overrun the volume, clears unsupported unwritten/refcounted flags.
- Leaf data extents are marked allocated or refcounted through `o2fsck_mark_tree_clusters_allocated()`.
- `o2fsck_check_extents()` wires inode-specific callbacks and also corrects directory `i_size` when extents describe less data than recorded; it clears indexed-dir state so pass 2 can rebuild indexes.

Dependencies: prompt framework, OCFS2 extent list/record helpers, refcount tracking, allocation bitmap marking, inode writeback helper.

Risk notes:
- Many fixes can truncate data or drop invalid subtree references, but every mutation goes through `prompt()`.
- The file deliberately treats read failures differently from bad extent-block magic.
- Directory index clearing does not directly free index blocks; later fsck accounting/reclaim is expected to handle them.
