# File Research: sources/os/linux/linux-stable/fs/btrfs/backref.c

## Summary
Implements Btrfs backreference walking, data-extent sharedness checks, inode/path resolution from extents, metadata backref iteration, and the backref cache used by relocation and related tree-block tracking.

## Main Responsibilities
- Finds leaves, roots, inodes, and paths that reference a logical extent.
- Merges delayed refs, inline refs, keyed refs, direct refs, and indirect refs.
- Resolves indirect refs by searching owner roots for parent blocks or file extent items.
- Determines whether a data extent is shared, with path and recent-extent caches.
- Converts logical addresses to extent items.
- Iterates tree-block backrefs in commit roots.
- Builds and maintains a bidirectional metadata backref cache of nodes and edges.

## Important Behavior
The core walk uses three preliminary-ref rbtrees: direct refs, indirect refs with keys, and indirect refs missing keys. Delayed refs are merged first when a transaction/time sequence is available. Inline and keyed refs from the extent tree are added next. Missing keys are filled by reading the referenced tree block, then indirect refs are resolved to parent bytenrs and merged into the direct tree.

For data extents, indirect refs identify inode, file offset, and root. `find_extent_in_eb()` scans file extent items in a leaf, filters by target disk byte and optionally by `extent_item_pos`, and builds inode element lists. `iterate_extent_inodes()` first finds referencing leaves, then finds all roots referencing each leaf, then invokes the caller iterator for each inode/offset/root tuple.

`btrfs_is_data_extent_shared()` short-circuits as soon as it proves sharing. It accounts for delayed add/drop refs, detects different inodes or roots, climbs parent tree blocks when sharing can come from snapshots, and caches path sharedness by tree level. It also has a small cache for recently checked data extents with multiple file extent items.

Path helpers walk `BTRFS_INODE_REF_KEY` and `BTRFS_INODE_EXTREF_KEY` items to produce filesystem-relative paths. Buffers are filled backward so callers can detect how much space was missing.

The backref iterator supports metadata backrefs in commit roots. It starts at an extent item, walks inline refs first, then keyed `TREE_BLOCK_REF` / `SHARED_BLOCK_REF` items.

The backref cache represents tree blocks as `btrfs_backref_node` objects and parent/child relationships as `btrfs_backref_edge` objects. Direct tree backrefs link to known parent bytenrs; indirect tree backrefs search the owner root to discover parents. Link finalization inserts newly discovered nodes into the cache and resolves pending edges breadth-first.

## State And Data Structures
- `extent_inode_elem` stores inode number, file offset, referenced byte count, and next pointer.
- `prelim_ref` stores root id, search key, level, ref count, inode list, parent, and wanted disk byte.
- `preftrees` separates direct, indirect, and missing-key preliminary refs.
- `share_check` tracks target inode/root, target data extent, share count, self refs, and delayed delete refs.
- `btrfs_backref_walk_ctx` carries the target bytenr, extent offset policy, transaction/time sequence, result ulists, caches, and callbacks.
- `btrfs_backref_share_check_ctx` caches path-level sharedness and recent data extent results.
- `btrfs_backref_cache`, `btrfs_backref_node`, and `btrfs_backref_edge` form the metadata backref cache.

## Risks
Backref walking is sensitive to transaction consistency. Mixing current delayed refs, tree mod log sequences, and commit-root searches incorrectly can report wrong owners or sharing. Negative delayed ref counts must merge with on-disk refs before early sharedness decisions. Inode lists are transferred between preliminary refs and ulists, so ownership must be nulled after transfer to avoid double free or use-after-free.

The backref cache has strict graph invariants: nodes must not be inserted twice, upper/lower edge lists must be symmetric after finalization, and error cleanup must walk pending edges and useless nodes without leaking or freeing cached nodes still in use.
