# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/refcount.c

Purpose: validates and repairs OCFS2 refcount trees and reconciles refcount records with refcounted extents discovered in files during pass 1.

Read coverage: complete file read, 1,098 lines.

Key responsibilities:
- Validates refcount block headers, generation, `rf_blkno`, parent/root fields, extent tree layout, record list counts, used counts, ordering, and cluster ranges.
- Builds an rbtree of refcount trees keyed by root block and tracks files attached to each tree.
- Records every refcounted extent encountered by pass 1 into per-file rbtrees.
- Removes invalid leaf refcount blocks from tree extent records when possible.
- Clears invalid refcount roots from inodes and removes `OCFS2_HAS_REFCOUNT_FL` when accepted by the user.
- Compares each physical cluster range claimed by refcounted file extents against corresponding refcount records.
- Updates refcount records to the actual number of files, removes redundant records, clears refcount flags, punches holes in refcount trees, or falls back to duplicate-cluster handling when repairs are declined.
- Marks refcounted clusters allocated so global allocation reconciliation sees shared physical clusters.

Important entry points:
- `o2fsck_check_refcount_tree()` validates and registers a file’s refcount tree during inode scanning.
- `o2fsck_mark_clusters_refcounted()` records refcounted extents from extent checking.
- `o2fsck_check_mark_refcounted_clusters()` performs final refcount reconciliation and frees all tracking structures.
- `check_rb()` validates a refcount block or refcount-tree block.
- `check_rl()` validates refcount record lists.
- `o2fsck_check_refcount()` reconciles one tree.
- `o2fsck_check_refcount_clusters()` and `o2fsck_check_clusters_in_refcount()` compare discovered extents to records.
- `o2fsck_remove_refcount_range()`, `o2fsck_refcount_punch_hole()`, `o2fsck_change_refcount()`, and `o2fsck_clear_refcount()` perform repair operations.

Dependencies:
- Uses libocfs2 refcount block read/write, refcount get/change/punch-hole, refcount flag manipulation, extent-list checking, cluster bitmaps, rbtree/list compatibility headers, and prompt problem codes.
- Cooperates with `extent.c` through `o2fsck_mark_clusters_refcounted()` callbacks and with pass 1 duplicate cluster tracking.

Risk and edge cases:
- The code allows an empty root refcount block but can invalidate empty non-root leaves.
- Refcount records must be monotonic by cluster; collisions or out-of-range references can be removed only if `rl_used` is trusted.
- When discovered refcount does not match the number of files and the user declines correction, clusters are marked duplicate and refcount metadata is removed/cleared to let duplicate repair handle them.
- Several internal assumptions are enforced with `assert()`, including prior tree/file registration and non-overlapping extent tuples.
- Root and leaf buffers are reread after libocfs2 refcount mutations because tree structure may change.
