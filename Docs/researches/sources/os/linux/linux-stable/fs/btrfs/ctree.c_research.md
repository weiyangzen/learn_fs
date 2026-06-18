# File Research: sources/os/linux/linux-stable/fs/btrfs/ctree.c

## Purpose
Implements core Btrfs B-tree operations: path allocation, root access, copy-on-write of tree blocks, key search, historical search through tree-mod-log state, node/leaf balancing, insertion, deletion, item resizing/splitting, and forward/backward iteration.

## Main Responsibilities
- Manage `struct btrfs_path` allocation, release, locking, and extent-buffer references.
- Safely acquire current root nodes under RCU and commit-root contexts.
- Perform copy-on-write of tree blocks with correct backreference updates.
- Search B-trees with correct read/write locking and restart behavior.
- Support searches over old tree versions using the tree modification log.
- Maintain B-tree shape by splitting, pushing, balancing, and promoting nodes/leaves.
- Insert, duplicate, split, extend, truncate, and delete leaf items.
- Maintain parent low keys after modifications to slot 0.
- Iterate to next/previous leaves and items.
- Initialize and destroy the path kmem cache.

## Key Logic
`btrfs_search_slot()` is the central search routine. It supports read-only lookup, insertion preparation, deletion preparation, COW searches, nowait reads, commit-root search, partial descent via `lowest_level`, and lock restarts through `-EAGAIN`.

`btrfs_cow_block()` validates transaction state, rejects COW on deleting roots, traces qgroup subtree state, and delegates to `btrfs_force_cow_block()` when required. Forced COW allocates a new tree block, copies contents, updates parent/root pointers, updates tree-mod-log records, frees old block references, and returns the new locked buffer.

`update_ref_for_cow()` is the backref-sensitive part of COW. It handles shared blocks, full backrefs, relocation roots, and last-ref cases, aborting the transaction on impossible reference state.

Node and leaf balancing helpers redistribute entries to siblings before splitting or deletion. `check_sibling_keys()` catches cross-block key ordering corruption that single-block tree checker validation cannot detect.

## Item Operations
- `btrfs_set_item_key_safe()` changes a leaf item key after verifying neighbor ordering.
- `btrfs_split_item()` splits one leaf item into two adjacent items.
- `btrfs_truncate_item()` shrinks item data from the end or front.
- `btrfs_extend_item()` grows item data in place.
- `btrfs_insert_empty_items()` and `btrfs_insert_item()` prepare and populate leaf items.
- `btrfs_duplicate_item()` duplicates an existing item under a new key in the same leaf.
- `btrfs_del_items()` compacts leaf item data, removes empty leaves, and tries to merge sparse leaves into neighbors.

## Iteration And Historical Views
- `btrfs_search_old_slot()` searches an old tree view using tree-mod-log rewind state.
- `btrfs_search_forward()` walks forward from a key while skipping nodes/leaves older than `min_trans`; defrag and tree logging use it.
- `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, and `btrfs_next_old_item()` advance current or historical tree iteration.
- `btrfs_previous_item()` and `btrfs_previous_extent_item()` walk backward with type/objectid filters.

## Locking And Risks
Slot 0 is special because changing the lowest key in a block requires updating parent keys up the tree. Many paths deliberately release locks and restart to avoid blocking I/O or changing lock requirements while holding unsafe locks.

Path flags such as `keep_locks`, `lowest_level`, `skip_locking`, `search_commit_root`, `need_commit_sem`, `nowait`, and `skip_release_on_error` materially alter search and ownership behavior.

Transaction mismatches during COW, bad relocation backrefs, zero refs, and sibling key order violations are treated as corruption and abort the transaction with `-EUCLEAN`.
