# File Research: sources/os/linux/linux/fs/hfsplus/brec.c

Purpose: Implements HFS+ B-tree record insertion/removal, node splitting, parent-key updates, and root height growth.

Key functions:
- `hfs_brec_lenoff()` and `hfs_brec_keylen()` decode record offsets/lengths and validate HFS+ two-byte key lengths.
- `hfs_brec_insert()` inserts key+entry data, splits full nodes, updates leaf count, and inserts new index records.
- `hfs_brec_remove()` removes records, unlinks empty nodes, and updates parent keys.
- `hfs_bnode_split()` allocates a sibling, chooses a split point, copies records, and updates sibling headers.
- `hfs_brec_update_parent()` adjusts ancestor separator key sizes/content after first-key changes.
- `hfs_btree_inc_height()` creates a new root and indexes the previous root.

Dependencies and integration:
- Mirrors the classic HFS `brec.c` design but uses HFS+ two-byte key lengths and treats the attributes tree as variable-index-key-like.
- Called by catalog, attributes, and extents mutation code.

Risk notes:
- Includes extra protection against oversized record offsets and key lengths.
- Removal does not clear obsolete offset/data bytes as thoroughly as the classic HFS version; correctness relies on `num_recs` and offset table bounds.
