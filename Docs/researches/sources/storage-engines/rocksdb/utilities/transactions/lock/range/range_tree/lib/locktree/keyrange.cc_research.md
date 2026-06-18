# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.cc

## Purpose
`keyrange.cc` implements the `toku::keyrange` endpoint pair used as the ordering key and interval payload in the range-lock tree.

## Important APIs, Types, And Functions
Implemented methods include borrowed creation, deep-copy creation, destruction, `extend()`, `get_memory_size()`, `compare()`, `overlaps()`, `get_infinite_range()`, endpoint accessors, and private copy-management helpers.

## Control Flow
`create()` borrows endpoint DBTs. `create_copy()` deep-copies endpoints, optimizing point ranges by storing one payload and making the right DBT reference the left copy. `compare()` returns `LESS_THAN`, `GREATER_THAN`, `EQUALS`, or `OVERLAPS` by comparing right-vs-left, left-vs-right, then both endpoints. `extend()` replaces left/right copies if the incoming range expands the current bounds.

## State And Persistence Behavior
A keyrange may either borrow endpoint pointers or own DBT copies in `m_left_key_copy` and `m_right_key_copy`. `destroy()` frees owned copies only. Infinite endpoints are represented by shared helper DBTs and are not copied. No disk state is written.

## Dependencies
It depends on the comparator wrapper and DBT helper functions such as `toku_clone_dbt`, `toku_destroy_dbt`, `toku_dbt_equals`, `toku_dbt_is_infinite`, and infinite endpoint factories.

## Integration Points
`treenode` copies keyranges into tree nodes, `locktree` constructs temporary requested/release ranges, and `range_buffer` serializes equivalent endpoints for transaction-owned lock lists and escalation callbacks.

## Risks And Edge Cases
Ownership is subtle: replacing one side of a point range must move the shared copy correctly. `get_memory_size()` ignores the point optimization and malloc overhead by design, so accounting is approximate. Callers must ensure borrowed DBTs outlive temporary operations.

## Test Signals
Comparator-specific range-lock tests cover key ordering. Conflict, consolidation, release, and escalation paths indirectly validate equality, overlap, and extend semantics.
