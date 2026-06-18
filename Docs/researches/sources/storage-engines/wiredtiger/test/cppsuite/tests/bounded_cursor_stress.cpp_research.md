# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_stress.cpp

## Purpose
Defines a comprehensive concurrent stress test for WiredTiger cursor bounds, covering bounded `search`, `search_near`, `next`, and `prev` while inserts, updates, removes, timestamps, and optional reverse collation are active.

## Important APIs, Types, And Functions
`class bounded_cursor_stress : public test` overrides `insert_operation`, `update_operation`, `read_operation`, and `custom_operation`. Key helpers include `custom_lexicographical_compare`, `set_random_bounds`, `validate_bound_search`, `validate_bound_search_near`, `validate_successful_search_near_inside_range`, `validate_successful_search_near_outside_range`, `validate_search_near_not_found`, `cursor_traversal`, and `cursor_traversal_walk`.

## Control Flow
`set_random_bounds` randomly clears bounds, sets lower, upper, or both, ensuring non-overlap when both are set and respecting reverse collator order. Insert threads add random keys. Update threads use random cursors to pick existing keys and update values. Read threads set random bounds, begin rounded timestamped read transactions, run bounded `search_near`, validate with a normal cursor, then validate bounded `search` on the returned key. Custom threads traverse forward and backward through bounded ranges and compare each key with a normal cursor positioned at the relevant bound.

## State And Persistence Behavior
The test persists random inserts and updates through standard worker CRUD and operation tracking. Read/custom validation uses read transactions with valid read timestamps where available. Cursor bounds are transient per cursor and reset or cleared as needed.

## Dependencies And Integration Points
Depends on `bound`, `bound_set`, constants, random generator, base test, timestamp manager, and operation tracker. It integrates reverse-collator configuration into comparison logic.

## Risks And Test Signals
The test has many assertion-heavy validation paths and tolerates `WT_ROLLBACK` in concurrent read/traversal branches. Reverse collator order changes bound comparisons, so `_reverse_collator_enabled` is captured at construction. Potential failure signals include returned keys outside bounds, normal/bounded cursor mismatch, traversal missing keys, or rollback retry exhaustion.
