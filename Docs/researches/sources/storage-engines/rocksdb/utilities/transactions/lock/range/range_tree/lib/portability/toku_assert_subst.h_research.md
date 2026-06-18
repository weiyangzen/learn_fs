# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_assert_subst.h

## Purpose
`toku_assert_subst.h` replaces PerconaFT's assertion macros with standard C/C++ assertions for the RocksDB port.

## Important APIs, Types, And Functions
It defines `assert_zero`, `invariant`, `invariant_notnull`, `invariant_zero`, lazy/paranoid variants, `ENSURE_POD(type)`, and `get_error_errno()`. In `NDEBUG`, core invariants compile to `(void)(a)`; paranoid variants still assert.

## Control Flow
The macros either evaluate to `assert(...)` checks or no-op casts depending on build mode. `get_error_errno()` asserts `errno` is nonzero and returns it.

## State And Persistence Behavior
There is no state. It only affects debug/release validation behavior.

## Dependencies
It includes `<assert.h>` and `<errno.h>`. `ENSURE_POD` assumes `<type_traits>` is available before use in C++ translation units.

## Integration Points
Nearly every range-tree file uses `invariant*` macros to enforce internal tree, OMT, locking, and memory assumptions.

## Risks And Edge Cases
Important safety checks vanish in release builds for non-paranoid invariants, so callers cannot rely on them for input validation. `ENSURE_POD` can fail compilation when classes gain constructors or non-trivial fields.

## Test Signals
Debug builds are important for catching tree and lock-request invariant violations. Release tests still need behavior checks because many defensive assertions are compiled out.
