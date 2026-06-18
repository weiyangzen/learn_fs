# File Research: sources/local-fs/e2fsprogs/e2fsck/ea_refcount.c

## Purpose
Implements a compact sorted-array refcount map used for extended attribute blocks, EA inode references, and quota accounting maps.

## Data Model
`struct ea_refcount` contains:
- count,
- allocated size,
- cursor for locality/iteration,
- sorted list of `(ea_key, ea_value)` elements.

Keys are `__u64` and can represent block numbers or inode numbers depending on caller.

## Main Behavior
- `ea_refcount_create()` allocates an initial list, defaulting to 500 entries.
- `get_refcount_el()` looks up by cursor fast path, then binary search, optionally inserting while preserving sorted order.
- `refcount_collapse()` removes zero-valued entries to reclaim slots.
- Public operations fetch, increment, decrement, store, return capacity, and iterate nonzero entries.
- Decrement rejects missing or already-zero values.

## Test Harness
Under `TEST_PROGRAM`, includes validation and a bytecode-like scripted test sequence for create/store/fetch/increment/decrement/collapse/list.

## Integration
Referenced from `e2fsck.h` and stored in `ctx->refcount`, `refcount_extra`, `ea_block_quota_*`, and `ea_inode_refs`.

## Risks / Notes
Insertions use `memmove`; performance is best for mostly sequential keys and modest map sizes. Zero stores remove logical entries only after later collapse.
