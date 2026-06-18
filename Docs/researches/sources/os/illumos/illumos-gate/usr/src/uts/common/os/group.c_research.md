# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/group.c

## Purpose

`group.c` implements a small generic kernel collection type, `group_t`, for storing pointer elements in a resizable array with iteration, indexed access, insertion/removal, and integer-list formatting support.

Read completely: 454 lines.

## Main Responsibilities

- Initializes and destroys `group_t` objects.
- Adds and removes pointer elements.
- Grows and shrinks the backing array in powers of two.
- Packs arrays after removal without preserving order.
- Supports pre-expansion and indexed insertion.
- Provides simple iterator state through `group_iter_t`.
- Converts groups of integer-like elements into compact range strings.

## Collection Semantics

`group_create()` zeroes a group. `group_destroy()` requires `grp_size == 0` and frees the backing set if allocated. `group_empty()` clears current entries but preserves capacity.

`group_add()` appends an element, optionally refusing to resize when `GRP_NORESIZE` is set. `group_remove()` searches for an element, nulls it, packs the set, decrements size, and can shrink capacity under `GRP_RESIZE`.

`group_expand()` grows capacity until it can hold at least a requested count.

## Storage Management

`group_grow_set()` doubles capacity or allocates the default capacity of 2. It copies old entries and frees old storage.

`group_shrink_set()` halves capacity down to the minimum default. It assumes capacity is a power of two and copies only the retained portion.

`group_pack_set()` moves later non-null entries into earlier holes. Element order is explicitly not preserved as a semantic guarantee.

## Access Helpers

`group_iter_init()` and `group_iterate()` provide sequential traversal over non-null entries up to `grp_size`.

`group_access_at()` returns the raw entry at an index, bounded by capacity. `group_add_at()` inserts at a specified index if capacity is sufficient and grows `grp_size` to include it. `group_remove_at()` clears an indexed slot. `group_find()` returns the index of a pointer or `(uint_t)-1`.

## Formatting

`group2intlist()` iterates group entries, maps each pointer through a caller-supplied converter, and emits compact integer ranges such as `1,2-5,8` into a caller buffer.

## Important Invariants

- Backing capacity is maintained as a power of two.
- `group_destroy()` expects the group to be logically empty.
- `group_add_at()` assumes the target slot is empty.
- The range formatter assumes iteration order is already meaningful for consecutive ID compression.

## Research Relevance

This is a general utility rather than a direct filesystem component. It is relevant as a shared kernel container used by subsystems that need small dynamic sets without list overhead.
