# File Research: sources/os/linux/linux/fs/btrfs/backref.c

Purpose: Implements Btrfs backreference walking, inode/path resolution from extents, data-extent sharedness checks, tree-backref iteration, and backref cache construction for relocation and generic tree analysis.

Major responsibilities:
- Resolve direct and indirect extent backrefs to parent tree blocks or roots.
- Merge on-disk inline/keyed refs with delayed refs from running transactions.
- Find all leaves or roots referencing a target extent.
- Iterate inodes and file offsets that reference a logical data extent.
- Convert inode refs/extrefs into filesystem-relative paths.
- Determine whether a data extent is shared for fiemap-like callers.
- Iterate metadata tree backrefs.
- Build and maintain a bidirectional backref cache used by relocation and related code.

Backref collection model:
- `struct btrfs_backref_walk_ctx` supplies the target `bytenr`, optional data offset filtering, transaction/time sequence, result ulists, and optional cache/callback hooks.
- Temporary refs are represented by `struct prelim_ref` and stored in three rbtrees: direct refs, indirect refs with keys, and indirect refs missing keys.
- `prelim_ref_insert()` merges identical refs and preserves negative counts from delayed drops so add/drop refs can cancel.
- `add_delayed_refs()` folds delayed refs whose sequence is within the requested tree-mod-log view.
- `add_inline_refs()` parses inline refs inside an extent item.
- `add_keyed_refs()` scans following keyed backref items for the same bytenr.
- `add_missing_keys()` reads tree blocks to obtain first keys for indirect metadata refs that lack keys.
- `resolve_indirect_refs()` turns indirect refs into concrete parent bytenrs, reinserting them as direct refs.

Core walking flow:
- `find_parent_nodes()` searches the extent tree for the target extent item, collects delayed/on-disk refs, resolves indirect refs, and emits parent bytenrs into `ctx->refs`.
- It supports commit-root searches, tree-mod-log time sequences, and active transactions.
- It can collect root IDs in `ctx->roots` when a ref has no parent and reaches a tree root.
- It attaches inode reference lists to leaf bytenrs for data extents unless `skip_inode_ref_list` is set.

Data extent handling:
- `find_extent_in_eb()` scans a leaf for non-inline `BTRFS_EXTENT_DATA_KEY` items pointing at `ctx->bytenr`.
- `check_extent_in_eb()` adjusts file offsets for bookend extents, honors `extent_item_pos` unless ignored, and records inode/offset/length triples.
- `iterate_extent_inodes()` finds referencing leaves, maps leaves to roots, and invokes a caller iterator for each inode reference.
- `iterate_inodes_from_logical()` maps a logical address to an extent, rejects metadata extents, and builds inode/root/offset triples.

Sharedness checks:
- `btrfs_is_data_extent_shared()` short-circuits as soon as it proves a data extent is shared or not shared.
- It accounts for delayed refs by attaching to the current transaction when possible; otherwise it uses `commit_root_sem`.
- `share_check` tracks references from other roots/inodes, self-reference counts, delayed delete refs, and data extent generation.
- It uses a path cache per tree level and a small previous-extents cache to speed repeated checks over nearby file extent items.
- It disables the path cache when multiple parent paths appear at a level.

Path and inode utilities:
- `btrfs_find_one_extref()` finds one extended inode reference item.
- `btrfs_ref_to_path()` walks parent inode refs backward and fills the caller buffer from the end.
- `iterate_inode_refs()` and `iterate_inode_extrefs()` enumerate regular and extended inode references.
- `paths_from_inode()` combines both ref styles into returned path strings.
- `init_data_container()` and `init_ipath()` allocate result containers for inode/path reporting.

Tree-backref iteration:
- `extent_from_logical()` maps a logical address to an extent item and returns whether it is data or metadata.
- `get_extent_inline_ref()` iterates inline refs inside an extent item.
- `tree_backref_for_extent()` extracts tree backref root/level pairs.
- `btrfs_backref_iter_start()` and `btrfs_backref_iter_next()` iterate metadata tree backrefs in commit root, supporting inline and keyed refs.

Backref cache:
- `btrfs_backref_init_cache()` initializes rbtrees/lists for cached tree block nodes and edges.
- `btrfs_backref_node` represents a tree block, including bytenr, owner, root, extent buffer, level, and state flags.
- `btrfs_backref_edge` links lower and upper tree blocks.
- Direct tree refs (`BTRFS_SHARED_BLOCK_REF_KEY`) are handled by `handle_direct_tree_backref()`.
- Indirect tree refs (`BTRFS_TREE_BLOCK_REF_KEY`) are resolved by searching the owning tree in `handle_indirect_tree_backref()`.
- `btrfs_backref_add_tree_node()` parses all backrefs for a tree block and queues parent edges.
- `btrfs_backref_finish_upper_links()` completes bidirectional parent/child links and inserts nodes into the cache rb tree.
- Cleanup helpers drop buffers, edges, nodes, pending edges, and useless detached nodes.

Risk notes: This is high-risk metadata code. Correctness depends on combining delayed refs, old tree views, direct refs, indirect refs, root ownership, and negative ref counts without double-freeing inode lists or missing shared paths. Error paths are extensive because corruption or missing extent roots must not produce false backref answers.
