# File Research: sources/os/linux/linux-stable/fs/btrfs/ulist.c

## Scope

This file implements `ulist`, a compact Btrfs utility structure for storing unique `u64` values with an auxiliary `u64`, supporting insertion, deletion, and enumeration. It is suited for graph/tree walks where recursion is undesirable due to kernel stack limits.

## Public And Internal APIs Covered

- Lifecycle: `ulist_init()`, `ulist_release()`, `ulist_reinit()`, `ulist_alloc()`, `ulist_prealloc()`, `ulist_free()`.
- Mutation: `ulist_add()`, `ulist_add_merge()`, `ulist_del()`.
- Iteration: `ulist_next()`.
- Internal RB-tree helpers search, insert, erase, and compare by `val`.

## Control Flow And Behavior

- Each node is linked into both a list and an RB tree. The RB tree enforces uniqueness and speeds lookup; the list drives iteration.
- `ulist_add_merge()` returns `0` if the value already exists, `1` if inserted, and `-ENOMEM` on allocation failure. If requested, it returns the old auxiliary value for existing entries.
- `ulist_prealloc()` reserves one node for later insertion, allowing callers to reduce allocation risk in constrained sections.
- `ulist_del()` removes an entry only when both `val` and `aux` match.
- `ulist_next()` advances a simple list iterator. Newly appended entries can appear in an ongoing traversal.

## State And Data Structures

- `struct ulist` tracks `nnodes`, list head, RB root, and one optional preallocated node.
- `struct ulist_node` carries `val`, `aux`, list linkage, and RB linkage.
- `struct ulist_iterator` stores the current list position only.

## Dependencies

- Linux slab allocation, lists, RB trees, and Btrfs assertion/message helpers.
- Caller-provided locking is required; write locking is needed for mutation and read locking is enough for iteration.

## Risks And Invariants

- The list and RB tree must stay synchronized for every insert/delete.
- `nnodes` is decremented with a `BUG_ON()` guard against underflow.
- Iteration order is intentionally unspecified and must not be treated as sorted or insertion-stable API.
