# File Research: sources/os/linux/linux-stable/fs/hfs/brec.c

## Scope

Implements classic HFS B-tree record mutation: record length/key-length discovery, leaf/index record insertion, record removal, node splitting, parent-key propagation, and tree-height growth.

## APIs And Behavior

- `hfs_brec_lenoff()` reads the record-offset table at the end of a bnode and returns record length plus start offset.
- `hfs_brec_keylen()` calculates keyed-record key length for leaf/index nodes, handling fixed index keys, variable index keys, and big-key validation against `tree->max_key_len`.
- `hfs_brec_insert()` inserts a key plus caller-supplied payload at `fd->record + 1`, splits the node if needed, updates leaf counts, shifts record offsets/data, and recursively inserts new child pointers into parent index nodes.
- `hfs_brec_remove()` removes the current record, compacts node data, unlinks empty nodes, removes parent index entries, and updates parent keys when the first key in a node changes.
- `hfs_bnode_split()` allocates a bmap node, divides records around the midpoint while accounting for the pending insert, rewrites sibling links, and updates `leaf_tail` when splitting the tail.
- `hfs_brec_update_parent()` replaces parent separator keys and may split index nodes if the replacement key grows.
- `hfs_btree_inc_height()` creates a new root node, turns an empty tree into a leaf tree, or creates an index root pointing at the old root.

## State And Dependencies

The file mutates `struct hfs_btree` root/depth/leaf counters, `struct hfs_bnode` sibling/parent/height/record metadata, and the on-disk node descriptor and record-offset table. It depends on `bnode.c` primitives, `bfind.c` search state, `btree.c` bmap allocation, and dirtying the B-tree inode when persistent tree metadata changes.

## Risks And Invariants

Record offsets grow upward from the node descriptor while record-offset slots grow downward from the end of the node; all insert/remove/split paths depend on preserving this layout exactly. Parent update paths temporarily reuse `fd->search_key` and `fd->bnode`, so reference ownership and restoration are subtle. If a split still cannot make room, the insert path panics, reflecting an assumed pre-reservation invariant.
