# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt_impl.h

## Purpose
Implements the OMT template declared in `omt.h`, including representation switching, balanced tree rebuilds, index arithmetic, binary searches, and mark cleanup.

## Important APIs, Types, And Functions
Implements all public `omt` methods plus internal helpers such as `create_internal`, `maybe_resize_array`, `convert_to_array`, `convert_to_tree`, `rebuild_from_sorted_array`, `insert_internal`, `delete_internal`, `iterate_internal`, `rebalance`, `find_internal_zero`, `find_internal_plus`, and `find_internal_minus`.

## Control Flow
Small append/prepend-like operations can stay in array form; middle insert/delete or mark support converts to tree form. Tree nodes store subtree weights, so index operations descend by comparing the target index with left weight. Rebalancing flattens a subtree to an index array and rebuilds it around median nodes. Root rebalance can convert through array form. Search in array mode uses binary search; tree mode recursively follows monotonic sign transitions.

## State And Persistence Behavior
State remains entirely in heap arrays owned by the OMT. `clear` resets counts without freeing capacity, while `destroy` frees the active representation. Tree `node_free` does not reuse nodes immediately; capacity pressure can force conversion/rebuild.

## Dependencies And Integration Points
Uses DB error constants such as `DB_KEYEXIST` and `DB_NOTFOUND`, Toku allocation wrappers, and invariant macros. OMT behavior directly affects locktree range ordering, owner lists, and escalation structures.

## Risks And Edge Cases
Mutation while marks exist is guarded by `barf_if_marked`, so callers must delete or clear marks before structural changes. `iterate_ptr` asserts callback success rather than propagating errors. Value memory is shallow-copied; pointer payload ownership is external. Recursive tree operations can be sensitive to corrupted weights.

## Test Signals
High-value tests include randomized comparison against `std::vector`, exact index validation after every mutation, mark consistency checks, rebuild/rebalance coverage, and binary search behavior for all sign-pattern cases.
