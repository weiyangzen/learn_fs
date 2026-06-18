# sources/storage-engines/foundationdb/fdbserver/workloads/ReportConflictingKeys.cpp

## Purpose
`ReportConflictingKeysWorkload` validates the `REPORT_CONFLICTING_KEYS` transaction option and the transaction special key range under `conflictingKeysRange`. It creates two transactions at the same read version, commits one with random write conflict ranges, and verifies that a conflicting second transaction reports key ranges consistent with its read conflict ranges and the first transaction's write conflict ranges.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `ReportConflictingKeys`. Important members include `keyForIndex`, `addRandomReadConflictRange`, `addRandomWriteConflictRange`, `emptyConflictingKeysTest`, and `conflictingClient`. It uses `ReadYourWritesTransaction`, `FDBTransactionOptions::REPORT_CONFLICTING_KEYS`, optional `READ_YOUR_WRITES_DISABLE`, `conflictingKeysRange`, `conflictingKeysTrue`, `conflictingKeysFalse`, and `validateSpecialSubrangeRead`.

## Control Flow
`start` clones the database and runs `conflictingClient` until `testDuration` expires. Each loop enables conflict reporting, verifies a fresh transaction has no conflicting keys, shares a read version between two transactions, commits `tr1`, then attempts to commit `tr2`. On `not_committed`, it reads `\xff\xff/transaction/conflicting_keys/`, checks local special-key read validation, and walks start/end marker pairs. If `tr2` commits, it independently verifies that no `tr2` read range intersected any `tr1` write range. Both transactions are reset after retries or success.

## State And Persistence Behavior
The workload writes no ordinary key values; it only manipulates transaction conflict ranges and observes resolver-produced conflict metadata exposed through special keys. Counters track invalid reports, commits, conflicts, and total completed transaction attempts. Conflict range vectors are local state cleared every loop.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWrites`, `SystemData`, tester workload registration, and `BulkSetup` key helpers. It disables `RandomRangeLock` because that workload intentionally causes range-lock conflicts that would invalidate this workload's conflict attribution assumptions.

## Risks And Edge Cases
The test assumes resolver conflict reporting returns merged ranges that contain at least one original read conflict range and intersect at least one write conflict range. It is sensitive to RYW conflict-range merging differences, special-key range prefix encoding, and the `TOO_MANY` limit. The source comments note it requires buggify and connection failure behavior to be disabled for reliable reporting.

## Test Signals
`check` passes only when `InvalidReports` is zero. Failure signals include `TestFailure` trace events for impossible missing conflicts, reported ranges that do not contain expected read ranges, reported ranges that do not intersect write ranges, and malformed special-key start/end marker pairs. Metrics expose transactions/sec, commits/sec, and conflicts/sec.
