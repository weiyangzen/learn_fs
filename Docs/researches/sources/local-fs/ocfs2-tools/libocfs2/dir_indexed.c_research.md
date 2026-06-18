# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_indexed.c

Implements OCFS2 indexed-directory support for userspace tooling.

Truncation clears `OCFS2_INDEXED_DIR_FL`, zeroes `i_dx_root`, writes the inode first, truncates non-inline DX trees, then deletes the DX root. Build path allocates a DX root, initializes directory trailers for all directory blocks, marks the inode indexed, inserts every existing dirent into the index via directory iteration, applies quota changes for DX leaf clusters, and rolls back with truncate on failure.

Directory trailer initialization verifies there is room for trailers without moving live entries, initializes trailer metadata, records each block’s largest free record, and threads free blocks through `dx_root->dr_free_blk`.

Hashing uses ext3-style TEA seeded from the OCFS2 superblock `s_dx_seed`; `.` and `..` hash to zero. Inline DX roots store entries in `dr_entries` until full, then `ocfs2_expand_inline_dx_root()` allocates one cluster of DX leaves, redistributes inline entries by minor-hash leaf index, clears inline flags, initializes root extents, and inserts the new cluster extent.

Lookup maps major hash through the DX root extent tree to a cluster/block and adds the minor-hash block index. Leaf rebalancing sorts entries, computes a split hash with special handling for all-same-major-hash leaves, allocates a new leaf cluster, inserts a new extent, and transfers entries above the split.

Insertion hashes a directory entry, expands/rebalances as needed, appends a DX entry to either root or leaf entry list, increments `dr_num_entries`, and writes root/leaf blocks. Search hashes the target name, scans matching DX entries, reads referenced directory blocks, validates entries, and returns an owned `ocfs2_dir_lookup_result`; `release_lookup_res()` frees its buffers.

The file also provides generic directory-entry validation/search helpers and DX entry removal by index.
