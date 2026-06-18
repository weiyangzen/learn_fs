# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-checker.h

## Summary
Declares Btrfs tree-checker status codes, parent-check input structure, valid block-group flag mask, and exported checker APIs.

## Main Responsibilities
- Define `struct btrfs_tree_parent_check` for owner/transid/first-key/level validation.
- Define `enum btrfs_tree_block_status` for clean and specific corruption classes.
- Define `BTRFS_BLOCK_GROUP_VALID` as the accepted block-group type/profile/remapped flag mask.
- Export leaf/node, chunk, owner, and parent key/level checker functions.

## Key APIs
- `__btrfs_check_leaf()` and `__btrfs_check_node()` return detailed `btrfs_tree_block_status` values.
- `btrfs_check_leaf()` and `btrfs_check_node()` wrap detailed checks as `0` or `-EUCLEAN`.
- `btrfs_check_chunk_valid()` validates chunk structures from either leaves or superblock sys-chunk arrays.
- `btrfs_check_eb_owner()` validates tree block owner compatibility.
- `btrfs_verify_level_key()` validates parent-provided level and optional first-key expectations.

## Important Behavior
`btrfs_tree_parent_check` allows owner and transid checks to be skipped with zero values, but documents that transid skipping should be limited to paths such as backref walking. `has_first_key` explicitly controls whether first-key matching is required.

The status enum separates structural failures such as invalid item counts, parent key mismatch, bad key order, invalid level/free space/offsets/block pointers/items/owner, and missing written flag.

## Risks
The header is part of the interface used by disk I/O, metadata validation, and btrfs-progs-compatible status reporting. Any enum or API behavior change can affect both kernel validation paths and users of detailed checker status codes.
