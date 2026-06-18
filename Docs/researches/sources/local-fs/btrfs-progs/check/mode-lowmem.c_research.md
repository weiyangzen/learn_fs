# File Research: sources/local-fs/btrfs-progs/check/mode-lowmem.c

## Scope

This file implements the low-memory Btrfs checker. It walks trees directly rather than building full in-memory indexes, validates fs-root item relationships, file extents, checksums, extent-tree backrefs, chunks, block groups, devices, and performs scoped repairs when `opt_check_repair` is enabled.

## Public Entry Points

- `check_fs_roots_lowmem()` checks fs/subvolume roots and root refs/backrefs.
- `check_chunks_and_extents_lowmem()` checks chunk, tree, extent, device, block-group, and backref consistency, then reconciles block accounting in repair mode.

## Major Internal Workflows

- Shared-node handling: `calc_extent_flag()`, `need_check()`, and `update_nodes_refs()` decide whether shared blocks need checking and whether full backrefs are expected.
- Repair safety: `avoid_extents_overwrite()` can allocate a fresh metadata chunk or exclude metadata blocks; `end_avoid_extents_overwrite()` cleans this state.
- Directory/ref validation: `find_dir_index()`, `find_dir_item()`, `find_inode_ref()`, `check_inode_ref()`, `check_inode_extref()`, and `check_dir_item()` cross-check dir items, dir indexes, inode refs/extrefs, inode items, file types, hashes, and duplicate names.
- Inode repair: recreates missing inode items, repairs mode, nlink, nbytes, dir isize, orphan items, generation/transid, and missing root-dir inode/ref cases.
- File extent validation: checks inline extent sizes, regular/prealloc types, generation bounds, checksum coverage, NODATASUM/compression rules, holes, alignment, symlink constraints, and data backrefs.
- Extent/backref validation: checks tree block refs, shared refs, data refs, inline-ref ordering, referencer existence, extent generation, crossing stripe boundaries, chunk type compatibility, and subpage alignment.
- Chunk/device/block-group validation: validates chunk stripes, dev extents, block-group items, device bytes used, device size boundaries, dev extent overlap, and super bytes-used accounting.
- Tree traversal: `walk_down_tree()` and `walk_up_tree()` perform bounded low-memory traversal with block validation, child-node checks, optional full tree item checks, and accounting.

## Repair Behavior

- Missing tree-block or data backrefs can be recreated by inserting extent items and incrementing refs.
- Bad referencer backrefs can be removed with `btrfs_free_extent()` or item deletion.
- Missing block-group items for chunks can be recreated.
- Missing device extents can be removed when repair is enabled.
- Block-group/super bytes-used errors are ultimately reconciled by `repair_block_accounting()`.
- Paths are re-searched after COW-affecting repairs.

## State And Accounting

- Static state: `last_allocated_chunk`, `total_used`, and `found_free_ino_cache`.
- Updates shared globals such as `bytes_used`, `total_btree_bytes`, `total_csum_bytes`, `data_bytes_allocated`, and `data_bytes_referenced`.
- Uses `g_task_ctx.item_count` during root traversal.

## Dependencies

- Depends heavily on Btrfs core tree search, extent/backref, transaction, csum, chunk/device, tree-checker, and repair APIs.
- Uses shared helpers from `mode-common.c` for csum counting, prealloc-written detection, imode repair, child validation, metadata exclusion, and device/super repair.

## Risks And Invariants

- Low-memory checking trades global indexes for careful tree walking; path validity after repair is a recurring concern.
- Shared tree blocks must only be fully checked/accounted once, while still validating referential integrity.
- Repair operations must avoid overwriting metadata being checked.
- Backref strictness changes for shared snapshots and full-backref parents; false strictness would misclassify valid shared extents.
- Some errors are fatal because continuing could loop, follow corrupt blocks, or operate on invalid item sizes.
