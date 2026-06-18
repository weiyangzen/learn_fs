# sources/storage-engines/badger/skl/skl_test.go

## Purpose
This test file validates the concurrent skiplist implementation in `skl.go`. It focuses on correctness of lookup/overwrite behavior, search boundary semantics, iterator traversal, concurrent insertion, large values, reference counting, and basic performance characteristics.

## Important Tests and Helpers
- `newValue`, `randomKey`, and `length` create deterministic values, random timestamped keys, and exact list length checks.
- `TestEmpty` validates empty `Get`, all `findNear` variants, iterator invalid states, and reference-counted close behavior.
- `TestBasic` checks insertion, timestamped lookup, overwrites for a logical key at a newer timestamp, metadata preservation, and values larger than `uint16`.
- `TestConcurrentBasic`, `TestConcurrentBasicBigValues`, and `TestOneKey` stress concurrent `Put`/`Get`, including many goroutines updating one key.
- `TestFindNear`, `TestIteratorNext`, `TestIteratorPrev`, and `TestIteratorSeek` verify exact search and traversal contracts.
- Benchmarks compare skiplist mixed read/write behavior to a locked map and measure concurrent writes.

## Control Flow and State Behavior
Tests build skiplists with a fixed arena size, insert timestamped keys using `y.KeyWithTs`, and assert results through `Get` and direct iterator reads. The refcount check in `TestEmpty` intentionally decrements the list before closing an iterator, proving the iterator's extra reference keeps the arena valid until `Close`.

Concurrent tests use `sync.WaitGroup` to launch many writers, then readers, and verify list length to ensure duplicate node insertion did not happen. The one-key test accepts nondeterministic final value but enforces that all observed values are from the valid write set and only one node remains.

## Dependencies and Integration Points
The tests use `testify/require`, Go's `sync`, `sync/atomic`, `rand`, and `testing` packages, plus Badger's `y` key helpers. They directly access unexported skiplist internals because they are in package `skl`.

## Risks and Edge Cases
The tests exercise concurrency but do not make outcomes deterministic enough to prove every interleaving. Benchmarks are not pass/fail correctness gates. The large-value tests validate arena value storage beyond small fixed widths, but they do not exhaust arena capacity failure behavior.

## Test Signals
The strongest behavioral signals are the `findNear` matrix for less/greater and equal/non-equal cases, iterator seek boundary checks before first/after last, and length assertions after concurrent duplicate-key writes.
