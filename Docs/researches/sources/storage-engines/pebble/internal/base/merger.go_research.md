# sources/storage-engines/pebble/internal/base/merger.go

Purpose: Defines the value merge abstraction used by Pebble's merge key kind, including a default append merger.

APIs and types: `Merge`, `ValueMerger`, `DeletableValueMerger`, `Merger`, `AppendValueMerger`, and `DefaultMerger`.

Control flow and state: A `Merge` creates a `ValueMerger` from an initial key/value. Merge operations are fed newer and older operands, then `Finish` returns a value and optional closer. `DeletableFinish` allows compaction to produce a deletion when merge semantics permit. `AppendValueMerger` concatenates values in correct order.

Persistence and dependencies: Merge results become persisted values in memtables/SSTables. Depends only on `io` for optional closers.

Integration points: Used by write path, iterators resolving merged values, and compaction. `test_utils.go` provides a deletion-capable test merger.

Risks: User merger ordering must match Pebble's newer/older operand calls. Returning closers requires callers to close resources. Merge implementations must not retain unstable byte slices unless copied.

Test signals: No direct test in this subset; merge behavior is exercised in higher-level DB and iterator tests.
