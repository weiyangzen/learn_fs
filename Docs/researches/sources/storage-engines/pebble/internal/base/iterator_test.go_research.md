# sources/storage-engines/pebble/internal/base/iterator_test.go

Purpose: Tests flag bitset helpers for seek operations.

APIs and types: Exercises `SeekGEFlags` methods for enabling/disabling `TrySeekUsingNext`, `RelativeSeek`, and `BatchJustRefreshed`, plus `SeekLTFlags.RelativeSeek` helpers.

Control flow and state: The test enumerates flag combinations and checks that helper methods set and clear only the intended bits.

Persistence and dependencies: No persistence. Uses basic testing and require-style checks.

Integration points: Protects small but important API used by batch, memtable, sstable, and merging iterators for seek optimization decisions.

Risks: Does not test actual iterator behavior under the flags; concrete iterator tests cover that.

Test signals: Good regression signal for flag composition and string output stability.
