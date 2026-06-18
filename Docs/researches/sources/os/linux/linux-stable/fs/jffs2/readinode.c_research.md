# File Research: sources/os/linux/linux-stable/fs/jffs2/readinode.c

This file reconstructs an in-memory JFFS2 inode from all non-obsolete raw node refs associated with an inode number.

Key responsibilities:
- Checks deferred data CRCs for unchecked data nodes in `check_node_data()`, using `mtd_point()` when possible, falling back to `jffs2_flash_read()`, and converting unchecked accounting to used accounting when data is valid.
- Maintains a temporary rb-tree of data nodes in `jffs2_add_tn_to_tree()`, discarding older nodes fully covered by newer valid nodes, handling version collisions, and marking overlap candidates for later resolution.
- Builds the final non-overlapping fragment tree in `jffs2_build_inode_fragtree()` by replaying overlapping groups in version order and adding valid full dnodes through `jffs2_add_full_dnode_to_inode()`.
- Reads dirent nodes in `read_direntry()`, validates node/name CRCs when needed, converts unchecked dirents to normal/deletion state, and accumulates full dirents.
- Reads inode data nodes in `read_dnode()`, validates node CRCs, performs lightweight or deferred data-CRC handling, recognizes zero-data metadata nodes, and inserts temporary dnodes.
- Handles unknown node compatibility policy in `read_unknown()`.
- Iterates all inode refs in `jffs2_get_inode_nodes()`, reading enough bytes for each node type, skipping obsolete refs safely under `erase_completion_lock`, and collecting highest version and latest directory mctime.
- Finalizes inode state in `jffs2_do_read_inode_internal()`: builds fragtree, chooses latest metadata, truncates regular files to latest `isize`, caches symlink targets, converts special-file data to metadata, and sets inocache state present.
- Provides public read, CRC-check, and clear paths through `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`.

Important interactions:
- Depends on scan-time inode caches and raw-node-ref lists built by `scan.c` or `summary.c`.
- Coordinates with inocache state machine values such as `UNCHECKED`, `CHECKING`, `GC`, `READING`, `PRESENT`, `CLEARING`, and `CHECKEDABSENT`.
- Calls xattr CRC/delete helpers during inode checking and clearing.

Notable invariants and risks:
- Obsolete raw refs may disappear after erase, so the next valid ref is found while holding `erase_completion_lock` before processing the current ref unlocked.
- Data CRC checking is intentionally deferred for write-buffered flash to avoid checking nodes later proven obsolete.
- Special files and symlinks are expected to have exactly one data fragment, which is moved into `f->metadata`.
- Root inode number 1 can be synthesized if no on-flash root inode exists.
