# File Research: sources/os/linux/linux/fs/jffs2/nodelist.c

This file implements JFFS2 in-core dirent lists, inode caches, fragment trees, raw node-ref chains, and related accounting helpers.

`jffs2_add_fd_to_list()` inserts full dirents sorted by name hash, replaces older same-name dirents by version, marks obsolete raw nodes when replacing, and frees discarded dirents.

Fragment-tree functions maintain the file logical extent map. `jffs2_lookup_node_frag()` returns the fragment covering an offset or the closest previous fragment. `jffs2_add_full_dnode_to_inode()` wraps a full dnode in a fragment and inserts it through `jffs2_add_frag_to_fragtree()`, which handles holes, overlap, splitting existing fragments, obsoleting fully covered fragments, and marking page-sharing nodes `REF_NORMAL` for GC scrutiny. `jffs2_truncate_fragtree()` removes fragments at/after a truncation size and marks/frees underlying dnodes as appropriate. `jffs2_kill_fragtree()` tears down an entire tree, optionally marking nodes obsolete.

`jffs2_obsolete_node_frag()` decrements a dnode’s fragment count, marking the raw node obsolete when no fragments remain or marking it normal when partially live. `new_fragment()` and `jffs2_fragtree_insert()` are local helpers for rb-tree insertion.

Inocache helpers manage sorted hash buckets. `jffs2_get_ino_cache()` looks up an inode cache; `jffs2_add_ino_cache()` assigns an inode number if needed and inserts; `jffs2_del_ino_cache()` removes and conditionally frees based on state; `jffs2_free_ino_caches()` releases all caches and xattr linkage.

Raw-node-ref helpers include `jffs2_free_raw_node_refs()`, `jffs2_link_node_ref()`, `jffs2_scan_dirty_space()`, and `__jffs2_ref_totlen()`. `jffs2_link_node_ref()` consumes a preallocated ref, verifies physical contiguity in the eraseblock, links it into the inode cache if present, and updates used/unchecked/dirty/free accounting based on ref flags. `__jffs2_ref_totlen()` computes node length from the next ref offset or eraseblock free boundary.

Key dependencies: rb-tree APIs, eraseblock accounting, raw node ref flags/macros from `nodelist.h`, allocation helpers, and obsolete-node handling in nodemgmt.

Important invariants: fragment trees must be gap-free except represented holes; raw refs in an eraseblock are physically ordered; superblock and eraseblock accounting is updated at the point refs are linked or dirty space is scanned.
