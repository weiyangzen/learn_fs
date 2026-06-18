# File Research: sources/local-fs/xfsprogs/db/btdump.c

Implements `btdump` / `b`, which prints a btree downward from the current cursor. It supports allocation/inode/rmap/refcount btrees, bmap btrees, inode btree roots, metadata inode btrees, directory da btrees, and attr da btrees. Option `-a` selects an inode’s attr fork, and `-i` includes internal node blocks.

Rather than duplicating print/address logic, it builds command strings and runs them through the normal interpreter (`print`, `addr`, `pop`). It handles short vs long btree block pointer formats, follows right siblings per level, descends through first child pointers, and uses separate operation tables for legacy/v3 attr and dir btrees. Loop guards stop when sibling traversal returns to the original or same daddr.
