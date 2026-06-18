# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_indices.cpp

## Purpose
Tests prefix-bounded `search_near` behavior in a unique-index-like insertion pattern and verifies duplicate-prefix insertion attempts fail without changing table cardinality.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_indices : public test` overrides `populate`, `insert_operation`, and `read_operation`. Static helpers include `perform_unique_index_insertions`, `populate_worker`, and `get_prefix_from_key`. State includes `prefixes_map`.

## Control Flow
Population creates collections, starts one populate worker per collection, and each worker inserts random prefixes using a sequence that inserts a prefix, removes it, applies prefix bounds, verifies `search_near` does not find an existing prefix, and inserts `prefix,id`. After population, it scans each collection into `prefixes_map`. Runtime insert threads pick existing prefixes and assert that the same unique-index insertion procedure fails. Read threads count records across all collections and assert total size remains equal to the populated prefix map size.

## State And Persistence Behavior
The test persists unique-index-shaped keys and tracks operations through the standard tracker. Runtime insert attempts intentionally roll back after verifying duplicate-prefix rejection. `prefixes_map` is in-memory state used for duplicate selection and cardinality validation.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, `thread_manager`, `connection_manager`, and the base test harness. It validates the bounded cursor prefix path against unique index semantics.

## Risks And Test Signals
Population retries rollbacks up to `MAX_ROLLBACKS`. `get_prefix_from_key` returns empty when no comma exists, so it assumes populated keys use the `prefix,id` shape. Read validation assumes each collection receives the same number of prefixes. Success is stable record count and failed duplicate-prefix insertions.
