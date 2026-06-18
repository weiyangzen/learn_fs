# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-mod-log.h

## Purpose

`tree-mod-log.h` declares the public Btrfs tree modification log interface. It exposes the sequence-blocker type, operation enum, and APIs used by B-tree update code and historical metadata readers.

## Main Interfaces

`struct btrfs_seq_list` represents one tree-mod-log user. Callers initialize it with `BTRFS_SEQ_LIST_INIT`, obtain a sequence with `btrfs_get_tree_mod_seq()`, and release it with `btrfs_put_tree_mod_seq()`.

`BTRFS_SEQ_LAST` is the sentinel maximum sequence value used for pruning and sequence comparisons.

`enum btrfs_mod_log_op` defines reversible mutation kinds:

- `BTRFS_MOD_LOG_KEY_REPLACE`
- `BTRFS_MOD_LOG_KEY_ADD`
- `BTRFS_MOD_LOG_KEY_REMOVE`
- `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_FREEING`
- `BTRFS_MOD_LOG_KEY_REMOVE_WHILE_MOVING`
- `BTRFS_MOD_LOG_MOVE_KEYS`
- `BTRFS_MOD_LOG_ROOT_REPLACE`

The file declares logging functions for key changes, node frees, root replacement, extent-buffer copy, key moves, root rewind, old-root lookup, old-root level lookup, and lowest active sequence lookup.

## Integration Role

This header is the contract between Btrfs tree mutation code and backref/history readers. Writers call insertion helpers around structural changes; readers hold a sequence blocker and later ask for old roots or rewound buffers.

## Dependencies And Constraints

The header forward-declares Btrfs types instead of including large internal headers, keeping compile dependencies low. It includes `<linux/list.h>` because `struct btrfs_seq_list` embeds `struct list_head`.

Correctness depends on callers using the enum values according to the actual mutation being performed. The implementation stores different fields for different operations, so mismatched operation types would make rewind unsafe.
