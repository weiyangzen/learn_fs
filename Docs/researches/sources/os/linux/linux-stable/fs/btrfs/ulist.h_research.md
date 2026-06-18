# File Research: sources/os/linux/linux-stable/fs/btrfs/ulist.h

## Scope

This header defines the Btrfs `ulist` data structures and function prototypes.

## APIs And Constants

- Defines `struct ulist_iterator`, `struct ulist_node`, and `struct ulist`.
- Declares lifecycle, preallocation, insertion/merge, deletion, and iteration functions.
- Provides `ulist_add_merge_ptr()` for storing pointer auxiliary data through the `u64 aux` field.
- Provides `ULIST_ITER_INIT()` to initialize iterators.

## Dependencies And Role

- Includes Linux integer types, lists, and RB trees.
- Used by Btrfs traversal code needing a uniqueness set with optional auxiliary state.

## Risks And Invariants

- `ulist_add_merge_ptr()` has a 32-bit compatibility path; callers must treat pointer auxiliary data carefully across architectures.
- The header documents that callers own locking; the implementation does not provide internal synchronization.
