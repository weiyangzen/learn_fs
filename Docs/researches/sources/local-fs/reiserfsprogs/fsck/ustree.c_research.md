# File Research: sources/local-fs/reiserfsprogs/fsck/ustree.c

Provides fsck-side wrappers around ReiserFS tree mutation and traversal. `reiserfsck_paste_into_item()`, `reiserfsck_insert_item()`, `reiserfsck_delete_item()`, and `reiserfsck_cut_from_item()` initialize a `tree_balance`, call `fix_nodes()`, then call `do_balance()` with the right mode.

Deletion and truncation paths free unformatted data blocks for indirect items before balancing:
- `free_unformatted_nodes()` walks indirect item block pointers and calls `reiserfs_free_block()`.
- `reiserfsck_cut_from_item()` frees the last unformatted node pointer being cut.

`pass_through_tree()` is a depth-first traversal from the root block. It reads each node, optionally calls an after-read callback, optionally calls a full-path callback for leaves or requested depth, skips subtrees with bad blocks or callback-reported problems, logs corruptions, and updates a spinner/progress display. It uses `bread()`, `brelse()`, path arrays sized by `MAX_HEIGHT`, and child pointers from internal nodes.
