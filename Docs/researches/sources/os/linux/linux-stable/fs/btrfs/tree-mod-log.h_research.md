# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-mod-log.h

## Scope

This header declares the Btrfs tree modification log interface used by tree mutation and old-root lookup paths.

## APIs And Constants

- Defines `struct btrfs_seq_list`, the per-user sequence-list element used to hold an active tree-mod-log read window.
- Provides `BTRFS_SEQ_LIST_INIT()` and `BTRFS_SEQ_LAST`.
- Defines `enum btrfs_mod_log_op` for key replacement/add/remove, remove while freeing, remove while moving, key moves, and root replacement.
- Declares all public tree-mod-log sequence, insertion, rewind, old-root, copy, move, free, and lowest-sequence helpers.

## Dependencies And Role

- Forward-declares Btrfs tree structures to keep the header lightweight.
- Included by Btrfs tree manipulation code that must emit log records before mutating internal tree blocks.

## Risks And Invariants

- Operation enum values encode the inverse replay cases implemented in `tree-mod-log.c`.
- `btrfs_seq_list.seq` must be initialized to zero before first registration, otherwise the user will not be added to the active list.
