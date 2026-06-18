# File Research: sources/local-fs/btrfs-progs/cmds/inspect-dump-tree.c

## Purpose
Implements `btrfs inspect-internal dump-tree`, a textual tree dumper for devices/images with options to dump selected trees, extents, roots, UUID tree, backup roots, or explicit tree blocks.

## Opening Strategy
The command opens ctree state with partial mode, no block groups, and skipped leaf item checks. This intentionally favors diagnostic visibility on damaged filesystems over strict validation.

## Explicit Block Dumping
- `dump_add_tree_block()` records each requested `--block` bytenr in a cache tree and rejects duplicates.
- `dump_print_tree_blocks()` checks sector alignment and verifies the logical address belongs to metadata before reading and printing each block.
- `--follow` can recursively print children of requested blocks.

## Tree Dumping Flow
- Without explicit blocks, it prints root/chunk/log root summaries or full trees depending on filters.
- It handles special roots not necessarily found through ordinary root items, such as root, chunk, log, and block-group trees.
- It scans root items from the tree root and log root tree, names known root object ids, applies filters for extent/device/uuid/tree-id modes, and prints either short root lines or full `btrfs_print_tree()` output.
- `--extents` uses `print_extents()` to recursively descend tree nodes and print leaves containing extent information.
- `--backups` prints superblock backup root slots via `print_old_roots()`.

## Options
Supports extent-only, device-only, roots-only, backup roots, UUID-only, one or more blocks, one tree id/name, device scan disabling, BFS/DFS traversal, hiding names, and checksum display modes.

## Notable Edge Cases
Child level mismatches in `print_extents()` are treated as corruption warnings and stop that branch. Explicit block mode requires only chunk-root availability and does not need full root setup.
