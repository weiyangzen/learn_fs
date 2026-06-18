# sources/storage-engines/wiredtiger/test/cppsuite/tests/burst_inserts.cpp

## Purpose
Implements a workload that simulates bursty bulk insertion with simultaneous random reads to create cache pressure.

## Important APIs, Types, And Functions
`class burst_inserts : public test` overrides `insert_operation`. It reads `_burst_duration` from configuration and uses a local `collection_cursor` struct containing collection reference, write cursor, and random read cursor.

## Control Flow
Each insert worker opens one write cursor and one `next_random=true` read cursor per assigned collection. For each collection, it inserts continuously for `_burst_duration` seconds without per-operation throttling, periodically commits when `can_commit` is true, walks the random reader to generate cache activity, then sleeps for the configured operation rate before moving to the next collection.

## State And Persistence Behavior
The workload persists many new keys, updates the in-memory collection key count after successful commits, and records operation-tracker entries through `thread_worker::insert`. Random reads do not persist data but can affect cache behavior.

## Dependencies And Integration Points
Depends on `random_generator` and base test. It uses the standard population, transaction, timestamp, and tracking machinery from `thread_worker`.

## Risks And Test Signals
The local struct's member order differs from its constructor parameter order, which is easy to misread, but initialization still places the normal cursor in `write_cursor` and the `next_random=true` cursor in `read_cursor`. Operational risks include `added_count` reset on rollback, large unthrottled bursts, and intentionally high cache pressure. Success is sustained commits and no unhandled cursor errors.
