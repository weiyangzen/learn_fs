# File Research: sources/local-fs/kdave-linux/fs/btrfs/backref.c

Purpose: Implements Btrfs backreference walking, inode/path resolution from extents, data-extent sharedness checks, tree-backref iteration, and relocation/generic backref cache construction.

Major responsibilities:
- Resolve direct and indirect extent backrefs to parent tree blocks or roots.
- Combine on-disk inline/keyed refs with delayed refs from active transactions.
- Find all leaves or roots referencing a target extent.
- Iterate all inodes that reference a logical data extent.
- Convert inode refs/extrefs into filesystem-relative paths.
- Provide metadata backref iteration for tree blocks.
- Maintain a bidirectional backref cache used by relocation and related code.

Core data flow:
- Backref collection starts from `btrfs_backref_walk_ctx` with `bytenr`, optional data offset filtering, fs info, transaction/time sequence, and optional callbacks.
- `find_parent_nodes()` searches the extent tree for the target extent item, folds delayed refs when a transaction/time sequence is available, adds inline refs, adds keyed refs, fills missing keys, resolves indirect refs, and emits parent bytenrs into `ctx->refs`.
- Temporary refs are stored as `struct prelim_ref` entries in three rbtree buckets: direct, indirect with keys, and indirect missing keys. Identical refs are merged and ref counts can become negative when delayed drops cancel existing refs.
- `resolve_indirect_refs()` searches owning roots to turn root/key/level references into concrete parent bytenrs, then reinserts them as direct refs.

Data extent handling:
- `find_extent_in_eb()` scans a leaf for `BTRFS_EXTENT_DATA_KEY` file extent items pointing to `ctx->bytenr`.
- `check_extent_in_eb()` adjusts file offsets for bookend extents, honors `extent_item_pos` unless ignored, and records inode/offset/length triples.
- `iterate_extent_inodes()` finds referencing leaves, maps leaves to roots, and calls the caller iterator for each inode reference.
- `iterate_inodes_from_logical()` maps a logical address to an extent and rejects metadata extents.

Sharedness checks:
- `btrfs_is_data_extent_shared()` determines whether a data extent is shared for fiemap-like callers.
- It short-circuits on multiple refs, refs from other roots/inodes, or known-not-shared generation checks.
- It accounts for delayed refs by joining/attaching to the current transaction when possible.
- It uses a path cache per tree level and a small previous-extents cache to accelerate repeated checks for nearby file extent items.
- It invalidates path-cache use when multiple parent paths appear at a level.

Path reconstruction:
- `btrfs_find_one_extref()` locates one inode extended reference.
- `btrfs_ref_to_path()` walks parent inode refs upward and writes a path backward into a caller buffer.
- `iterate_inode_refs()` and `iterate_inode_extrefs()` gather regular and extended inode refs.
- `paths_from_inode()` populates an `inode_fs_paths` container with all available paths, tracking missed paths and missing bytes when the buffer is too small.

Extent helpers and iterators:
- `extent_from_logical()` locates the extent item containing a logical address and reports whether it is data or metadata.
- `tree_backref_for_extent()` iterates tree block refs from an extent item.
- `btrfs_backref_iter_start()` and `btrfs_backref_iter_next()` iterate metadata backrefs in the commit root, covering inline refs and keyed refs; data extents return `-ENOTSUPP`.

Backref cache:
- `btrfs_backref_init_cache()`, allocation/free helpers, and cleanup helpers manage `btrfs_backref_node` and `btrfs_backref_edge` objects.
- `btrfs_backref_add_tree_node()` reads tree block backrefs, handles direct shared-block refs and indirect tree-block refs, and marks nodes checked.
- `handle_direct_tree_backref()` links to parent bytenr directly or identifies reloc-root self refs.
- `handle_indirect_tree_backref()` searches the owner root path to discover parent blocks, creates intermediate nodes/edges, and skips known unshareable paths.
- `btrfs_backref_finish_upper_links()` completes bidirectional linkage and inserts new nodes into the cache rb tree.
- `btrfs_backref_error_cleanup()` unwinds pending edges and useless nodes after partial build failure.

Concurrency and consistency:
- Uses transaction handles, tree-mod-log sequence numbers, `commit_root_sem`, delayed-ref locks/mutexes, and path `search_commit_root`/`skip_locking` choices to obtain consistent views.
- Handles `BTRFS_SEQ_LAST` specially for qgroup commit-time use: delayed refs are skipped and commit roots are searched.
- Uses `cond_resched()` in large loops to avoid long non-preemptible walks.

Error and corruption handling:
- Common errors include `-ENOMEM`, `-ENOENT`, `-EINVAL`, `-EIO`, `-EUCLEAN`, and `-ENOTSUPP`.
- Invalid inline ref types return `-EUCLEAN`.
- Extent keys with impossible offset `-1` are treated as corruption.
- Missing extent roots are logged and return `-EUCLEAN`.
- Several invariants use `ASSERT`, `WARN_ON`, `BUG_ON`, and `btrfs_backref_panic()` for internal inconsistency.

Risk notes: This is complex correctness-critical code. Delayed-ref merging, negative ref counts, sharedness early exits, and path-cache validity are subtle; mistakes can misreport shared extents, miss roots, leak/free inode lists incorrectly, or break relocation cache topology.
