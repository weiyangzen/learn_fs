# File Research: sources/os/linux/linux-stable/fs/hfs/bfind.c

## Scope

This file implements HFS B-tree search cursor setup/teardown, binary search within a node, root-to-leaf traversal, record reading, and cursor movement across leaf nodes.

## Public And Internal APIs Covered

- `hfs_find_init()` allocates search/key buffers and locks the appropriate B-tree mutex subclass.
- `hfs_find_exit()` releases the current node, frees search buffers, and unlocks the tree.
- `__hfs_brec_find()` binary-searches one node for the best record not greater than the search key.
- `hfs_brec_find()` traverses from the root down index nodes to a leaf.
- `hfs_brec_read()` finds and reads a record body.
- `hfs_brec_goto()` moves the cursor by record count, crossing previous/next leaf links.

## Control Flow And Behavior

`hfs_find_init()` rejects null inputs, allocates enough memory for search and result keys, stores two key buffers in one allocation, logs the caller, and locks the catalog, extents, or attributes tree with a lockdep subclass based on CNID. Unknown tree CNIDs return `-EINVAL`.

`__hfs_brec_find()` performs a binary search over node records using `hfs_brec_lenoff()`, `hfs_brec_keylen()`, `hfs_bnode_read()`, and the tree's key comparator. It records the selected record number, key offset/length, entry offset, and entry length. It returns `0` for exact matches, `-ENOENT` for best-less-than-only results, and `-EINVAL` for zero-length keys.

`hfs_brec_find()` clears cursor offsets, starts at `tree->root`, and walks `tree->depth` levels. Each node is loaded with `hfs_bnode_find()`, checked for expected height and type, assigned a parent, and searched. Index entries provide the next child node number. On invalid height/type or unusable index result it releases the node and returns an error.

`hfs_brec_goto()` moves relative to the current record. Negative movement walks `prev` leaf links; positive movement walks `next` links. It then refreshes offsets and reads the current key into `fd->key`.

## Dependencies

This file depends on HFS B-tree structures, node cache/loading, record layout helpers, key comparators, and per-tree mutexes.

## Risks And Invariants

The caller must pair `hfs_find_init()` with `hfs_find_exit()`. The tree lock protects the cursor and B-tree shape during traversal. Node validation enforces expected type/height by depth, but record length/key validation is limited to the helpers and zero-key checks. `hfs_brec_find()` returns `-ENOENT` even with a valid best-fit cursor, so callers must distinguish exact-match needs from traversal needs.
