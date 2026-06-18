# File Research: sources/local-fs/btrfs-progs/kernel-lib/rbtree_augmented.h

## Purpose
Augmented red-black tree support: callbacks and erase/insert helpers that maintain caller-defined subtree metadata.

## Key Interfaces
- `struct rb_augment_callbacks` with `propagate`, `copy`, and `rotate`.
- `rb_insert_augmented()`, `rb_insert_augmented_cached()`.
- `RB_DECLARE_CALLBACKS(...)` macro to generate standard augmentation callbacks.
- Internal color/parent helpers and `__rb_erase_augmented()`.
- `rb_erase_augmented()`, `rb_erase_augmented_cached()`.

## Dependencies
Includes `kernel-lib/rbtree.h`.

## Notable Behaviors
- Insert expects caller to update augmented data on the path before calling the augmented insert helper.
- Erase copies augmentation data to successor nodes and propagates updates upward.
- Cached erase updates `rb_leftmost` before rebalancing.

## Risks
- Public comments warn that most definitions are implementation details; external users should depend only on callback structs and augmented insert/erase APIs.
- Incorrect `propagate/copy/rotate` callbacks silently break data structures such as interval trees.
