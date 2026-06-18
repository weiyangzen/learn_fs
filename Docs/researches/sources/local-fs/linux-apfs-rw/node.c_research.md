# File Research: sources/local-fs/linux-apfs-rw/node.c

## Purpose
Implements APFS b-tree node storage, validation, lookup within nodes, record insertion/replacement, node splitting, free-space management, and node creation/deletion.

## Main Responsibilities
- Reads APFS b-tree nodes from virtual, physical, or ephemeral storage.
- Verifies node checksums and node table-of-contents bounds to protect against crafted filesystems.
- Creates empty b-tree roots for supported physical trees and creates/deletes nonroot nodes.
- Maintains in-memory node metadata and writes it back to on-disk node headers.
- Locates key/value byte ranges for fixed-size and variable-size node formats.
- Parses keys for catalog, omap, free queue, extentref, fext, snapshot metadata, and omap snapshot queries.
- Executes bisection searches, previous/next iteration, exact and multiple-record node-local queries.
- Extracts omap mappings from successful omap queries.
- Increases b-tree height, splits nodes, creates single-record nodes for huge catalog records, and attaches new children to parents.
- Manages fragmented key/value free lists, node defragmentation, TOC expansion, record insertion, and record replacement.

## Key Functions
- `apfs_read_node()`: maps an object ID to a block or ephemeral object, reads node metadata, validates it, and returns an `apfs_node`.
- `apfs_make_empty_btree_root()`: allocates and initializes an empty root node and info footer for supported b-tree subtypes.
- `apfs_delete_node()`: frees catalog/omap/extent/snapshot physical nodes or ephemeral free-queue nodes according to query type.
- `apfs_node_locate_key()` / `apfs_node_locate_value()`: convert TOC entries into checked block offsets and lengths.
- `apfs_node_query()`: searches a node and prepares query offsets for b-tree traversal.
- `apfs_btree_inc_height()` and `apfs_node_split()`: handle growth and split propagation for insertions.
- `apfs_node_has_room()`, `apfs_node_insert()`, `apfs_node_replace()`: implement space checks and record mutation.
- `apfs_defragment_node()` and free-list helpers: rebuild fragmented nodes through temporary full-node copies.

## Dependencies
Uses APFS object mapping, spaceman block allocation/free queues, omap record creation/deletion, transactions, checksums, b-tree query structures from `apfs.h`, and key parsers from `key.c`.

## Notes
The implementation explicitly handles APFS quirks such as root info footers, backward-counted value offsets, fixed key/value TOCs, free-queue ghost records, ephemeral objects, and huge catalog values that may require one-record nodes.
