# sources/storage-engines/tikv/components/tidb_query_common/src/storage/ranges_iter.rs

Purpose: provides a small state machine over user key ranges for scanners. It tells callers whether to start a new range, continue the current interval, or stop.

Important APIs and control flow: `IterStatus` has `Drained`, `NewRange(Range)`, and `Continue`. `RangesIterator` owns an `IntoIter<Range>` and an `in_range` flag. `next` returns `Continue` while a range is active; otherwise it pops the next range or returns drained. `notify_drained` clears the active flag. `is_drained` checks whether no further ranges remain.

State and persistence behavior: in-memory iteration state only. Multiple `notify_drained` calls are idempotent.

Dependencies and integration: `scanner.rs` uses it to coordinate storage `begin_scan`, point gets, and interval `scan_next_entry` calls.

Risks and test signals: `is_drained` ignores `in_range`, so it means "no queued ranges after the current one" rather than "all scanning is complete"; scanner uses that nuance for scanned-range boundary calculations. Tests cover empty/nonempty iteration, continuation, and repeated drain notifications.
