
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tracking.rs

## Purpose
`TrackingBlockStore` is a testutils wrapper that counts low-level operations while delegating behavior to an underlying store. It supports performance-style tests that assert an algorithm touches only expected blockstore APIs.

## Important APIs, Types, and Functions
- `ActionCounts` records counters for `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, `all_blocks`, `remove`, `try_create`, and `store`.
- `ActionCounts` derives `Add`, `AddAssign`, and `Sum`; `ZERO` is the all-zero constant.
- Custom `Debug` prints only nonzero fields.
- `TrackingBlockStore::new(underlying)` wraps an async-drop guarded store and initializes `Mutex<ActionCounts>`.
- `counts()` returns the current count snapshot.
- `get_and_reset_counts()` returns the snapshot and resets to zero.
- Reader/deleter/writer trait implementations increment the matching counter and then delegate.

## Control Flow
Every public low-level method locks the counter mutex, increments a field, releases the lock at the end of the statement, and calls the underlying store. `allocate()` is static and not counted because no wrapper instance is involved. `store_optimized()` and `try_create_optimized()` count as `store` and `try_create` respectively.

## State and Persistence Behavior
The only wrapper state is the in-memory counter mutex plus the owned underlying store. Async drop delegates to the underlying store; counters are not persisted.

## Dependencies and Integration Points
Composes over any optimized low-level blockstore. Exported only for tests/testutils. Used by tests that need operation counts and by the common low-level test suite to ensure functional pass-through.

## Risks and Edge Cases
- Uses `std::sync::Mutex` in async methods, but only for a short synchronous increment before awaiting.
- `allocate()` calls are invisible to counters.
- Counting begins before delegate success/failure, so failed operations are counted too; tests rely on this.

## Test Signals
Local tests instantiate the common low-level suite and specifically assert counter behavior for each method, failed `try_create`, missing `remove`, optimized writer methods, overhead calls, all-blocks stream creation/collection, and `get_and_reset_counts()`.
