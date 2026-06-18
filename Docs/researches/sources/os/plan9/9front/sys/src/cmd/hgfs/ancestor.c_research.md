# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/ancestor.c

Finds a common Mercurial ancestor revision hash through a mounted `hgfs` tree.

Key points:
- Defines temporary `XNode` records with hash, traversal mark, hash-table link, and queue link.
- Uses a 256-bucket hash table keyed by the first hash byte.
- Handles equal hashes and `nullid` inputs as fast paths.
- Performs alternating breadth-first expansion from `xhash` and `yhash`.
- Reads each revision’s `rev1` and `rev2` files from the mounted `hgfs` namespace to discover parents.
- Stops when a node already marked from the opposite side is found.
- Returns `nullid` when no common ancestor exists.
- Frees all allocated traversal nodes before returning.

Dependencies and interactions:
- Uses `readhash()` and `%H` formatting from `hash.c`.
- Depends on `hgfs` exposing revision directories with `rev1` and `rev2`.

Research relevance:
- Ancestor discovery utility used by the update/merge planner in `hgdb.c`.
