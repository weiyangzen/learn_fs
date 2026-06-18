# sources/storage-engines/wiredtiger/test/cppsuite/tests/hs_cleanup.cpp

## Purpose
Defines a workload intended to age out full pages and drive history store cleanup by repeatedly updating ranges of existing keys at advancing timestamps.

## Important APIs, Types, And Functions
`class hs_cleanup : public test` overrides `update_operation`.

## Control Flow
Each update thread asserts the number of collections equals the number of threads, selects the collection matching its thread id, opens one cursor, then loops while running. It sleeps, begins a transaction if needed, advances the cursor, resets at `WT_NOTFOUND`, rolls back on `WT_ROLLBACK`, copies the current key, updates it with a random pseudo-random value, and commits when `can_commit` is true.

## State And Persistence Behavior
The test persists repeated value updates over existing keys and records them through the operation tracker. Advancing timestamps from `thread_worker::update` should create obsolete historical versions that history store cleanup can remove when globally visible.

## Dependencies And Integration Points
Depends on logger/random generator and the base test. Validation and statistic monitoring are expected to be provided by the framework configuration, especially metrics monitor stats referenced in the file comment.

## Risks And Test Signals
The comment notes key range uncertainty, so the workload walks sequentially rather than targeting precise ranges. It asserts fewer than 100 rollback retries. The retrieved key pointer is passed to update; the comment says it should be copied for buffer validity, but the code passes `key_tmp` directly to a `std::string` parameter, which copies at call construction. Success is sustained updates and expected history-store cleanup statistics externally.
