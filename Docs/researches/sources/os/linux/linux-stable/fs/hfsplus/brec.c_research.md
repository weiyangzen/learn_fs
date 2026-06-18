# File Research: sources/os/linux/linux-stable/fs/hfsplus/brec.c

## Scope

Implements HFS+ B-tree record insertion/removal, node splitting, parent key updates, and height growth.

## APIs And Behavior

- `hfs_brec_lenoff()` reads record length and offset from the bnode offset table.
- `hfs_brec_keylen()` returns fixed index key length for non-variable non-attribute index nodes, otherwise validates and returns the big-key length from the record itself.
- `hfs_brec_insert()` inserts `fd->search_key` plus entry payload, splits full nodes, updates leaf counts, shifts offsets/data, and recursively inserts index records for split nodes.
- `hfs_brec_remove()` removes the current record, unlinks empty nodes, removes parent index records, compacts data, and updates parent keys for first-record changes.
- `hfs_bnode_split()` allocates a new bnode, chooses a split point based on half-node data and record-offset table size, copies upper records, updates sibling descriptors, and handles tail updates.
- `hfs_brec_update_parent()` replaces parent separator keys, splitting index nodes if the new key is larger.
- `hfs_btree_inc_height()` creates a new root and installs the old root as an index child when needed.

## State And Dependencies

The file depends on HFS+ bnode primitives, `hfs_bmap_alloc()`, `hfs_brec_find()` strategy callbacks, tree dirtying, and attributes-tree special key semantics.

## Risks And Invariants

Unlike classic HFS, HFS+ keys use big-key 16-bit lengths and attributes-tree index keys are treated as variable even when tree flags differ. Split failure unlinks the newly allocated node before returning `-ENOSPC`. Cursor mutation and reference transfers mirror classic HFS and require careful `hfs_bnode_put()` pairing.
