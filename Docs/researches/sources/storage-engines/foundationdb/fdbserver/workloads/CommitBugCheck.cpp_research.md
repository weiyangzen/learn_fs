# sources/storage-engines/foundationdb/fdbserver/workloads/CommitBugCheck.cpp

## Purpose
`CommitBugCheck.cpp` defines `CommitBug`, a regression workload for two commit-related bugs. It repeatedly verifies that sequential commits preserve final value semantics and that retry behavior around conflicts, `transaction_too_old`, and unknown commit-style errors does not produce skipped or duplicated counter values.

## Important APIs, Types, And Functions
The main type is `CommitBugWorkload : TestWorkload`, registered as `CommitBug`. It exposes actors `bug1` and `bug2`, uses `Transaction`, `tr.set`, `tr.get`, `tr.clear`, `tr.commit`, `tr.reset`, `tr.onError`, and checks error codes such as `commit_unknown_result`, `not_committed`, and `transaction_too_old`.

## Control Flow
`start` runs `bug1(cx, this) && bug2(cx, this)` under a 60-second timeout. `bug1` loops forever writing `Value1`, then `Value2`, then reading the key to ensure `Value2` is present, then clearing it. `bug2` iterates 1000 counter increments; each iteration reads the current value, ensures it equals the expected loop index, writes `i + 1`, and commits. On non-conflict/non-too-old errors, it resets and retries just the set/commit path.

## State And Persistence
Each client uses keys `B1Key<clientId>` and `B2Key<clientId>`. `bug1` clears its key every loop. `bug2` leaves the final counter value after completion. Workload state is the boolean `success`.

## Dependencies And Integration Points
The workload depends on FDB transaction retry semantics and tester parallel actor composition. It is designed to run under simulation faults that produce ambiguous commit results and conflicts.

## Risks
The `start` timeout returns `Void` even if the actors are still looping, so success depends on `success` being flipped on detected failure before check. `bug2` treats errors other than `not_committed` and `transaction_too_old` by retrying the write after reset without re-reading, which is intentional for the regression but relies on idempotence of setting the expected next value. Trace-only `CODE_PROBE`s mark expected rare error paths.

## Test Signals
Failure traces are `CommitBugFailed` and `CommitBug2Failed`; retry diagnostics include `CommitBugSetVal1Error`, `CommitBugSetVal2Error`, `CommitBugGetValError`, `CommitBugClearValError`, and `CommitBug2Error`. `check` returns `success`.
