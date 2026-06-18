# File Research: sources/local-fs/btrfs-progs/check/repair.h

## Purpose
Declares repair-mode globals, corrupt-block records, and repair helper functions used by btrfs check.

## Exposed Types and Globals
- `extern int opt_check_repair` indicates repair mode.
- `struct btrfs_corrupt_block` combines a `cache_extent`, first key, and level for corrupt tree-block tracking.

## API
Declares corrupt extent recording, block accounting rebuild, tree/used block marking, orphan dev-extent removal, block checking for repair, unsafe item-key update, and low-key fixup.

## Dependencies
Includes `tree-checker.h`, `btrfs_tree.h`, and `common/extent-cache.h`, with forward declarations for btrfs transaction, fs info, paths, roots, extent IO trees, and extent buffers.
