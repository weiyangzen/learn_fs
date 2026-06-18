# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_search_near.cpp

## Purpose
Validates that prefix-bounded `search_near` returns keys consistent with unbounded `search_near` under concurrent random inserts.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_search_near : public test` overrides `populate`, `insert_operation`, and `read_operation`. Private validation helpers are `validate_prefix_search_near`, `validate_successful_calls`, and `validate_unsuccessful_prefix_call`.

## Control Flow
Population only creates empty collections. Insert threads distribute collections across workers and insert random alphabetic keys with random values in timestamped transactions. Read threads choose random collections, begin a rounded read transaction at a valid read timestamp when available, generate random prefixes, apply `bound_set(prefix)`, call bounded `search_near`, then open a default cursor and validate bounded results against unbounded search-near behavior.

## State And Persistence Behavior
Writers persist random keys and operation tracker rows. Readers use read timestamps and rollback read transactions after their target operation count. Bounds are applied per cached cursor and reset after use.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, `timestamp_manager`, and base test. It exercises WiredTiger cursor bounds, search-near exact values, and timestamp visibility.

## Risks And Test Signals
Concurrent inserts can make visibility dependent on read timestamp; the test mitigates timestamp invalidation with `roundup_timestamps=(read=true)` and skips `read_timestamp=0`. Validation has detailed branches for bounded success, bounded not found, exact values, and neighboring keys. Success is absence of assertion failures.
