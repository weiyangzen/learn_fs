# File Research: sources/local-fs/btrfs-linux/fs/btrfs/backref.c

Implements Btrfs backreference walking, extent-to-inode/root/path resolution, sharedness checks, and backref cache graph construction.

Key points:
- Backref walking represents discovered references as `prelim_ref` records stored in rbtrees.
- Maintains separate trees for:
  - Direct refs with known parent bytenr.
  - Indirect refs with enough key/root information to resolve.
  - Indirect refs missing keys that require reading the child block.
- `add_prelim_ref()`, `add_direct_ref()`, and `add_indirect_ref()` merge equivalent refs and track reference counts, including negative delayed-drop refs.
- Delayed refs are integrated through `add_delayed_refs()`, accounting for add/drop actions and ref types.
- On-disk extent refs are parsed through:
  - `add_inline_refs()` for inline refs inside extent items.
  - `add_keyed_refs()` for separate keyed backref items.
- `add_missing_keys()` reads tree blocks to obtain first keys when indirect metadata refs lack keys.
- `resolve_indirect_ref()` resolves `(root_id, key, level)` to parent logical addresses by searching the appropriate fs root or old tree state.
- `find_parent_nodes()` is the core engine: it gathers delayed/on-disk refs, resolves indirect refs, merges parents, optionally collects roots, and optionally attaches inode lists for data refs.
- `btrfs_find_all_leafs()` finds leaves containing file extent items pointing to a target data extent.
- `btrfs_find_all_roots()` recursively walks metadata parents to identify all roots that reference an extent.
- `btrfs_is_data_extent_shared()` is optimized for fiemap-like sharedness checks:
  - Stops early when sharing is proven.
  - Accounts for delayed refs when a transaction can be joined.
  - Uses path-cache entries for repeated leaf/path checks.
  - Caches recent extent sharedness when the same bytenr appears in multiple file extent items.
- `extent_from_logical()` maps a logical address to the containing extent item and returns whether it is data or tree block metadata.
- `iterate_extent_inodes()` resolves a data extent to inode/file-offset/root tuples, using optional leaf-to-root caches.
- `iterate_inodes_from_logical()` is a logical-address-to-inode helper for ioctl-style reporting.
- Path reconstruction:
  - `btrfs_find_one_extref()` iterates extended inode refs.
  - `btrfs_ref_to_path()` walks parent inode refs backward into a path string.
  - `paths_from_inode()` combines regular inode refs and extended refs.
  - `init_data_container()` and `init_ipath()` allocate output containers.
- Tree backref iteration:
  - `btrfs_backref_iter_alloc()`, `btrfs_backref_iter_start()`, and `btrfs_backref_iter_next()` iterate inline/keyed metadata backrefs in commit root.
  - `tree_backref_for_extent()` extracts tree backref root/level information.
- Backref cache graph:
  - `btrfs_backref_node` represents tree blocks.
  - `btrfs_backref_edge` connects child and parent tree blocks.
  - `btrfs_backref_cache` stores nodes in an rb tree plus pending/useless lists.
  - `btrfs_backref_add_tree_node()` processes direct and indirect tree backrefs for a node.
  - Direct shared block refs use parent bytenr directly.
  - Indirect tree block refs search the owning root to find parent blocks.
  - `btrfs_backref_finish_upper_links()` finalizes bidirectional graph linkage.
  - Cleanup paths carefully release buffers, roots, edges, and detached nodes.

Role in system:
- This is central to Btrfs’s COW/reference model. It supports qgroups, fiemap shared-extent reporting, logical inode lookup, send/receive style ancestry needs, relocation, scrub/repair decisions, and consistency checking.
- The code handles multiple tricky states: delayed refs, old tree-mod-log views, commit-root searches, shared subtree detection, data reloc roots, skinny metadata, and negative refs from pending drops.
