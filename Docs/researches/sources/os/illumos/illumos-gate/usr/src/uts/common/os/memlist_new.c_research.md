# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/memlist_new.c

## Purpose

Implements allocation/free-list support and sorted span manipulation for `struct memlist` lists. These lists describe physical memory address ranges such as installed or available memory.

This file is a small foundational utility used by memory configuration code and boot/runtime memory-list management.

## Main Responsibilities

- Maintain a global freelist of reusable `struct memlist` nodes.
- Insert preallocated blocks of `struct memlist` nodes into the freelist.
- Insert existing nodes into sorted non-overlapping memory lists.
- Find the memlist element containing an address.
- Add spans with adjacency coalescing and overlap rejection.
- Delete spans with trimming, whole-node removal, or node splitting.

## Key Data

- `memlist_freelist`
  Singly linked list of free `struct memlist` nodes.

- `memlist_freelist_count`
  Count of free nodes.

- `memlist_freelist_mutex`
  Protects freelist and count.

## Key Functions

- `memlist_get_one(void)`
  Pops one node from the freelist. Caller must handle `NULL`.

- `memlist_free_one(struct memlist *mlp)`
  Pushes one node onto the freelist.

- `memlist_free_list(struct memlist *mlp)`
  Pushes an entire linked list of nodes onto the freelist and counts them.

- `memlist_free_block(caddr_t base, size_t bytes)`
  Treats a raw memory block as an array of `struct memlist` nodes and adds them all to the freelist.

- `memlist_insert(struct memlist *new, struct memlist **curmemlistp)`
  Inserts a caller-provided node into sorted order. Panics if the list is overlapping or malformed.

- `memlist_del(struct memlist *memlistp, struct memlist **curmemlistp)`
  Unlinks a specific node from a doubly linked memlist. Debug builds assert that the node is present.

- `memlist_find(struct memlist *mlp, uint64_t address)`
  Returns the node containing `address`, or `NULL`.

- `memlist_add_span(uint64_t address, uint64_t bytes, struct memlist **curmemlistp)`
  Allocates a node and adds a span. It coalesces with adjacent nodes, can concatenate two adjacent ranges, rejects overlaps with `MEML_SPANOP_ESPAN`, and returns `MEML_SPANOP_EALLOC` on node allocation failure.

- `memlist_delete_span(uint64_t address, uint64_t bytes, struct memlist **curmemlistp)`
  Deletes an existing span. It rejects missing/partially missing spans, trims from front/back, removes whole nodes, or splits a node when deleting from the middle.

## Return Codes

- `MEML_SPANOP_OK`
  Operation succeeded.

- `MEML_SPANOP_ESPAN`
  Add overlaps an existing span, or delete targets a span not fully present.

- `MEML_SPANOP_EALLOC`
  A new memlist node was needed but unavailable.

## Locking and Synchronization

Only the node freelist is internally locked. The actual memory lists passed by `curmemlistp` are not globally locked here; callers must hold the appropriate memlist lock, such as `memlist_write_lock()`, when manipulating shared lists.

## Invariants

- Managed memory lists are sorted by `ml_address`.
- Managed memory lists are non-overlapping.
- Adjacent spans are coalesced by `memlist_add_span()`.
- Doubly linked `ml_prev`/`ml_next` pointers are maintained for active lists.
- Free-list linkage uses `ml_next`; other fields may retain old values until reused.

## External Dependencies

Used by physical memory configuration code for `phys_install`, `phys_avail`, and related span bookkeeping.

## Research Notes

The subtle point is allocation ownership: `memlist_add_span()` allocates its own node from the freelist, while `memlist_insert()` inserts a supplied node. Callers must distinguish these APIs and must provide external locking for shared active lists.
