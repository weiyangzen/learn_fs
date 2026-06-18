# File Research: sources/os/linux/linux/fs/btrfs/print-tree.c

This file implements diagnostic printing for Btrfs tree blocks, leaves, keys, and selected item payloads. It is debug/inspection code, not metadata mutation logic.

Primary exported functions:
- `btrfs_root_name()` maps known root object IDs to readable names, with special formatting for tree relocation roots.
- `btrfs_print_leaf()` prints a leaf header and decodes each item by key type.
- `btrfs_print_tree()` prints node/leaf structure and can recursively follow child pointers.

Important helpers:
- `print_chunk()` and `print_dev_item()` decode chunk/device metadata.
- `print_extent_item()` decodes extent items, tree block info, and inline backrefs.
- `print_extent_data_ref()` and `print_extent_owner_ref()` print full/simple quota backref ownership data.
- `print_uuid_item()` validates and prints UUID-tree payload subvolume IDs.
- `print_raid_stripe_key()` prints RAID stripe tree stride device/physical pairs.
- `print_inode_item()`, `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` decode common fs-tree records.
- `print_extent_csum()` derives checksum coverage from checksum size and sectorsize.
- `print_file_extent_item()` distinguishes inline file extents from regular/prealloc mappings.
- `key_type_string()` maps many Btrfs key types to readable strings, including qgroup, RAID stripe, and remap keys.

Behavior:
- `btrfs_print_leaf()` emits header metadata, optional debug extent-buffer ref/lock state, then dispatches each item slot by key type.
- Known payload types are decoded enough to correlate logical keys with on-disk fields.
- Directory/xattr records print structural metadata but not names or values.
- `btrfs_print_tree()` prints node keys and child block pointers; with `follow=true`, it reads child blocks using `btrfs_tree_parent_check`, validates levels, recurses, and releases child buffers.

Safety and validation:
- Extent item size is checked before dereferencing.
- Shared refs warn on parent bytenrs not aligned to sectorsize.
- UUID items reject payloads not aligned to `u64`.
- Recursive traversal validates expected child level, transid, owner root, and first key.
- Uses `BUG()` for impossible child level mismatches during diagnostic traversal.

Dependencies:
- Uses Btrfs accessors from `accessors.h`.
- Uses metadata definitions from `ctree.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Uses tree IO helpers from `disk-io.h`.
