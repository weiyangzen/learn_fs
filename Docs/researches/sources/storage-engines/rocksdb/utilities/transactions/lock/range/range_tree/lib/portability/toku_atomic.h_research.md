# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_atomic.h

## Purpose
`toku_atomic.h` provides typed wrappers around GCC `__sync_*` atomic builtins with cache-line boundary assertions and poisons direct builtin use after wrapper definitions.

## Important APIs, Types, And Functions
Helpers include `which_cache_line()`, `crosses_boundary()`, `toku_sync_fetch_and_add()`, `toku_sync_add_and_fetch()`, `toku_sync_fetch_and_sub()`, `toku_sync_sub_and_fetch()`, `toku_sync_val_compare_and_swap()`, and `toku_sync_bool_compare_and_swap()`.

## Control Flow
Each wrapper asserts the target object does not cross an assumed 64-byte cache line, then calls the matching `__sync_*` builtin. The final `#pragma GCC poison` list prevents accidental direct builtin calls in files that include this header.

## State And Persistence Behavior
The wrappers mutate caller-owned scalar fields atomically; no persistent state exists. `locktree` uses them for reference counts, memory counters, and STO score updates.

## Dependencies
It includes boolean, size, integer headers and `toku_assert_subst.h`.

## Integration Points
`toku_portability.h` includes this header, so many locktree files receive these wrappers transitively. Manager memory accounting and locktree reference counting are the main users.

## Risks And Edge Cases
The old `__sync_*` builtins are full-barrier primitives and less expressive than modern `std::atomic`. The cache-line assertion is approximate and assumes 64-byte lines. Poisoning can surprise code that includes this header before third-party headers using builtins.

## Test Signals
Concurrent reference-count and memory-accounting stress tests are the best signals. Compilation also verifies no forbidden direct builtins appear after inclusion.
