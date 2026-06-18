# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_rangeset.c

## Purpose

`subr_rangeset.c` implements a compact non-overlapping interval set for kernel consumers. It stores `struct rs_el` ranges in a PCTRIE keyed by `re_start`, with half-open intervals `[re_start, re_end)`. The implementation supports insertion, removal, predicate-filtered removal, lookup by containing address, exact-start lookup, emptiness checks, copying, full destruction, and DDB inspection.

## Main Data Model

The public `struct rangeset` owns:

- `rs_trie`: PCTRIE of `rs_el` nodes.
- `rs_dup_data`: caller-supplied clone function used when a removal splits an existing range or when copying.
- `rs_free_data`: caller-supplied destructor for range payloads.
- `rs_data_ctx`: callback context.
- `rs_alloc_flags`: UMA allocation flags used by pctrie node allocation.

`rs_el` storage itself is supplied by callers through the `data` argument to `rangeset_insert()`. The file treats `data` as `struct rs_el *`, fills `re_start` and `re_end`, and inserts it.

## Initialization And Allocation

`rs_rangeset_init()` creates a UMA zone named `"rangeset pctrie nodes"` sized by `pctrie_node_size()`. The zone is installed by `SYSINIT(rs, SI_SUB_LOCK, SI_ORDER_ANY, ...)`.

`rs_node_alloc()` recovers the owning `struct rangeset` from the embedded pctrie and allocates trie nodes using that rangeset’s allocation flags. `rs_node_free()` frees trie nodes back to the zone. `PCTRIE_DEFINE(RANGESET, rs_el, re_start, ...)` generates the typed trie operations.

## Core Operations

`rangeset_init()` initializes the trie and callback fields. `rangeset_fini()` validates the set under `DIAGNOSTIC` and removes all ranges.

`rangeset_check_empty(rs, start, end)` looks up the range with greatest start less than or equal to `end`; the interval is empty if no such range exists or that range ends at or before `start`.

`rangeset_insert(rs, start, end, data)` first removes any overlapping existing ranges, then inserts the provided node as `[start, end)`. This makes insertion replace overlap rather than fail on overlap.

`rangeset_remove_pred(rs, start, end, pred)` is the important algorithm. It walks backward using `LOOKUP_LE(end - 1)` and handles all interval-overlap cases:

- Existing range ends before `start`: stop.
- Existing range lies fully inside removal span: remove and free it if predicate passes.
- Removal cuts the right side of an existing range: shrink `re_end` to `start`.
- Removal cuts the left side of an existing range: remove/reinsert with `re_start = end`.
- Removal cuts a hole in the middle: duplicate the node, insert the right fragment, and shrink the original left fragment.

If split allocation fails, it returns `ENOMEM` and leaves the original range intact. Predicate false means the matching range is preserved and iteration adjusts around it.

`rangeset_remove()` uses an always-true predicate. `rangeset_remove_all()` reclaims the full trie and calls the user free callback for each leaf.

`rangeset_containing(rs, place)` returns a range whose `re_start <= place < re_end`. `rangeset_beginning(rs, place)` returns only an exact-start range. `rangeset_empty(rs, start, end)` checks for any range beginning after `start` but before `end`; unlike `rangeset_check_empty()`, it does not call diagnostic validation and is start-key oriented.

`rangeset_copy(dst, src)` requires an empty destination and matching duplicate callback, clones each source node in ascending order, and cleans up the destination on failure.

## Invariants And Diagnostics

Under `DIAGNOSTIC`, `rangeset_check()` iterates in ascending start order and asserts:

- `re_start < re_end`.
- Neighbor ranges do not overlap: previous `re_end <= current re_start`.

The DDB `show rangeset <addr>` command prints the rangeset pointer and every element’s start/end pair.

## Dependencies

Key dependencies are `sys/pctrie.h`, `sys/rangeset.h`, UMA allocation, and optional DDB support.

## Maintenance Notes

The code assumes callers serialize access externally; no locks are embedded in `struct rangeset`. Any future caller must also provide correct lifetime callbacks because range payload memory belongs to the caller, while internal trie-node memory belongs to this file.

Split-removal is the highest-risk path: it depends on `rs_dup_data()` preserving all payload fields other than `re_start/re_end`, and on `rs_free_data()` correctly releasing failed duplicate nodes.
