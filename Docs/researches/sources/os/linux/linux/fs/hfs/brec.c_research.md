# File Research: sources/os/linux/linux/fs/hfs/brec.c

Purpose: Implements low-level HFS B-tree record mutation: record length/key length decoding, insertion, deletion, node splitting, parent-key propagation, and root height growth.

Key functions:
- `hfs_brec_lenoff()` reads the offset table at the end of a node to derive record offset and length.
- `hfs_brec_keylen()` decodes fixed or variable HFS keys, including big-key handling and max-key validation.
- `hfs_brec_insert()` inserts a key+entry pair into a leaf or index node, splitting nodes and recursively adding index records when needed.
- `hfs_brec_remove()` removes a record, compacts node data/offset tables, unlinks empty nodes, and removes parent index records.
- `hfs_bnode_split()` allocates a B-tree node, moves upper records, relinks leaf/index sibling pointers, and adjusts the active search cursor.
- `hfs_brec_update_parent()` updates ancestor separator keys after first-record changes.
- `hfs_btree_inc_height()` creates a new root when the tree grows.

Dependencies and integration:
- Depends on `btree.h` node I/O helpers, bitmap allocation, search cursor state, and `__hfs_brec_find()`.
- Called by catalog and extent code through `hfs_brec_insert()`/`hfs_brec_remove()`.
- Marks the B-tree inode dirty when leaf counts, root, tail, or node metadata change.

Risk notes:
- Correctness depends on exact offset-table arithmetic and even-sized key layout.
- Error paths around parent updates and split recursion can leave partially modified B-tree structures if callers do not reserve nodes first.
- The code uses `panic("not enough room!")` if a split still cannot fit the record, so malformed trees or reservation bugs can escalate hard.
