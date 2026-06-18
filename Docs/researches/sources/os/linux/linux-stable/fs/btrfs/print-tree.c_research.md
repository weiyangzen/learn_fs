# File Research: sources/os/linux/linux-stable/fs/btrfs/print-tree.c

This file implements Btrfs diagnostic tree/leaf printing helpers. It does not mutate filesystem state; it formats in-memory `extent_buffer` contents into kernel log output with `pr_info()`, `pr_cont()`, `btrfs_info()`, warnings, and debug-only reference/lock details.

Main responsibilities:
- Map well-known root object IDs to readable names through `root_map[]` and `btrfs_root_name()`.
- Print B-tree leaves item-by-item via `btrfs_print_leaf()`.
- Print internal nodes and optionally recurse through children via `btrfs_print_tree()`.
- Decode common item payloads: inode items, directory items, inode refs/extrefs, file extents, checksums, roots, extents/backrefs, block groups, chunks, devices, UUID items, persistent/temporary items, RAID stripe tree items, and remap items.
- Convert item key types to readable strings through `key_type_string()`.

Important functions:
- `btrfs_root_name()` returns symbolic names for core roots like `ROOT_TREE`, `EXTENT_TREE`, `CHUNK_TREE`, `QUOTA_TREE`, `RAID_STRIPE_TREE`, etc.; relocation roots include the offset in the supplied buffer.
- `print_extent_item()` validates extent item size, prints refs/generation/flags, tree block info when present, then walks inline refs and formats each ref type. It warns about shared block/data parent offsets not aligned to sectorsize.
- `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` iterate packed variable-length records inside one item.
- `print_file_extent_item()` distinguishes inline extents from regular/prealloc extents and prints disk bytenr, disk bytes, logical offset, logical bytes, ram bytes, generation, type, and compression.
- `print_raid_stripe_key()` prints each `btrfs_raid_stride` using `btrfs_num_raid_stripes()` from `raid-stripe-tree.h`.
- `btrfs_print_tree()` prints a node header and child keys. If `follow` is true, it reads each child with `read_tree_block()` and a `btrfs_tree_parent_check`, verifies the level relationship, recursively prints it, then frees the child buffer.

Key dependencies:
- Btrfs accessors and item layout definitions from `ctree.h`, `accessors.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Tree block validation via `tree-checker.h`.
- Tree block reads via `disk-io.h`.

Notable invariants and edge handling:
- `btrfs_print_leaf()` returns immediately for a null buffer.
- `print_extent_item()` rejects extent items smaller than `struct btrfs_extent_item`.
- UUID items must be `u64` aligned in size.
- Unknown key types print as `UNKNOWN.<type>`.
- Recursive `btrfs_print_tree()` uses `BUG()` if child level relationships are inconsistent after a successful read.
- `print_eb_refs_lock()` only emits refcount/lock owner/current pid under `CONFIG_BTRFS_DEBUG`.

Role in the subsystem:
- This is a debug/inspection aid for Btrfs metadata. It centralizes readable formatting for tree dump paths used during diagnostics, corruption analysis, and development.
