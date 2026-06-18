# File Research: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.c

This file implements debug/diagnostic printing for Btrfs tree blocks, leaves, keys, and selected item payloads. It is not filesystem mutation logic; it is used to inspect on-disk metadata structures through `pr_info()`, `pr_cont()`, and `btrfs_info()` logging.

Primary exported functions:
- `btrfs_root_name()` maps root object IDs to readable names, with special formatting for tree relocation roots.
- `btrfs_print_leaf()` prints one leaf extent buffer and decodes many item types.
- `btrfs_print_tree()` prints a node or leaf and can recursively follow child block pointers.

Important internal helpers:
- `print_chunk()` prints chunk length, owner, type, and stripe device/offset records.
- `print_dev_item()` prints device item ID, total bytes, and bytes used.
- `print_extent_item()` decodes extent items, including tree block info and inline refs.
- `print_extent_data_ref()` and `print_extent_owner_ref()` print data and simple-quota owner refs.
- `print_uuid_item()` decodes UUID-tree payloads as subvolume IDs and validates `u64` alignment.
- `print_raid_stripe_key()` prints RAID stripe tree stride device/physical pairs.
- `print_inode_item()`, `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` decode common fs-tree records.
- `print_extent_csum()` reports checksum item logical range based on checksum and sector sizes.
- `print_file_extent_item()` distinguishes inline file extents from regular/prealloc extent mappings.
- `key_type_string()` maps Btrfs item key types to readable strings, including qgroup, RAID stripe, and remap keys.

Behavior and control flow:
- `btrfs_print_leaf()` prints the leaf header, optional debug extent-buffer ref/lock state, then iterates every item slot and dispatches by key type.
- For known item types it prints enough structured fields to correlate logical keys with payload metadata.
- It intentionally prints directory/xattr item records without dumping names or values.
- `btrfs_print_tree()` prints node headers and child pointers. If `follow` is true, it reads each child with a `btrfs_tree_parent_check`, validates level consistency, recurses, and frees the child extent buffer.

Safety and validation:
- `print_extent_item()` validates item size before dereferencing `struct btrfs_extent_item`.
- Shared block/data refs warn if parent bytenr is not sector-size aligned.
- `print_uuid_item()` rejects UUID items whose payload size is not `u64` aligned.
- Recursive tree following uses `read_tree_block()` with expected level, transid, owner root, and first-key checks.
- The code uses `BUG()` for impossible child level mismatches during diagnostic traversal.

Dependencies:
- Relies heavily on accessor helpers from `accessors.h`.
- Uses metadata definitions from `ctree.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Uses `read_tree_block()` and extent-buffer lifetime helpers from tree/disk IO code.
