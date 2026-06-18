# File Research: sources/os/linux/linux/fs/jffs2/readinode.c

## Role

Reconstructs an in-memory JFFS2 inode from all non-obsolete raw node refs associated with an inode number.

## Key Responsibilities

- Checks deferred data CRCs for unchecked data nodes in `check_node_data()`, using `mtd_point()` when possible and falling back to `jffs2_flash_read()`.
- Converts valid unchecked accounting into used accounting and marks bad unchecked nodes obsolete.
- Maintains a temporary rb-tree of data nodes in `jffs2_add_tn_to_tree()`, discarding older fully covered nodes, handling version collisions, and marking overlap groups.
- Builds the final non-overlapping fragment tree in `jffs2_build_inode_fragtree()` by replaying overlap groups in version order.
- Reads and validates dirent nodes in `read_direntry()`, including name CRC validation when needed.
- Reads and validates data nodes in `read_dnode()`, including deferred data-CRC strategy for write-buffered flash.
- Handles unknown compatible/incompatible node types in `read_unknown()`.
- Iterates all inode refs in `jffs2_get_inode_nodes()`, safely finding the next valid ref under `erase_completion_lock` before processing the current one unlocked.
- Finalizes inode state in `jffs2_do_read_inode_internal()`: chooses latest metadata, truncates regular files to latest `isize`, caches symlink targets, moves special-file data into `f->metadata`, and marks the inocache present.
- Provides public read, CRC-check, and clear paths through `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`.

## Important Interactions

- Depends on scan-time inode caches and raw-node-ref lists from `scan.c` or `summary.c`.
- Coordinates with inocache states: unchecked, checking, GC, reading, present, clearing, and checked-absent.
- Calls fragment-tree helpers, xattr CRC/delete helpers, inode-cache state helpers, and node-obsoletion helpers.

## Invariants and Risks

- Obsolete refs may disappear after erase, so traversal obtains the next valid ref while holding `erase_completion_lock`.
- Data CRC checking is intentionally deferred for write-buffered flash to avoid checking nodes later proven obsolete.
- Root inode 1 may be synthesized if absent on flash.
- Symlinks and special files are expected to have exactly one data fragment, which becomes metadata.
