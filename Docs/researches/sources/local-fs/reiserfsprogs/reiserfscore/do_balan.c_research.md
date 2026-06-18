# File Research: sources/local-fs/reiserfsprogs/reiserfscore/do_balan.c

Core execution phase for ReiserFS tree balancing after `fix_nodes()` has analyzed required shifts, joins, splits, and allocated buffers. It mutates leaf/internal nodes according to the `tree_balance` plan.

Key behavior:
- `balance_leaf_when_delete()` handles delete/cut. It removes or truncates the affected item, updates delimiting keys when first items change, joins with left/right neighbors when requested, invalidates emptied buffers, and frees their blocks.
- `balance_leaf()` handles insert/paste. It shifts content to left and right neighbors, handles whole or partial movement of inserted/pasted data, treats directory entries and indirect items specially, updates key offsets after partial splits, inserts into new split nodes from FEB buffers, and prepares promoted keys/pointers for internal balancing.
- `make_empty_leaf()` and `make_empty_node()` initialize formatted nodes.
- `get_FEB()` obtains and initializes an empty buffer from `tb->FEB`.
- `replace_key()` copies a leaf or internal key into a parent delimiting-key slot and marks the parent dirty.
- `reiserfs_invalidate_buffer()` marks a node free, forgets cached state, and returns the block to the bitmap.
- Neighbor-position helpers map path positions to parent child slots.
- `do_balance()` coordinates leaf balancing, then calls `balance_internal()` for higher levels while `insert_size[h]` remains nonzero, and finally `unfix_nodes()` releases fixed buffers.

The file embodies the classic ReiserFS policy: leaf shifts pack nodes aggressively, deletion can merge nodes, and internal balancing is delegated upward with promoted keys and child pointers.
