# sources/storage-engines/foundationdb/fdbserver/workloads/TxnTimeout.cpp

## Purpose
`TxnTimeout` validates transaction lifetime behavior in simulation by running read-modify-write transactions that intentionally remain open for at least `txnMinDuration` while avoiding false failures during recovery-related version jumps.

## Important APIs, Types, and Functions
The workload uses `Transaction`, `SERVER_KNOBS->MAX_READ_TRANSACTION_LIFE_VERSIONS`, `MAX_WRITE_TRANSACTION_LIFE_VERSIONS`, `VERSIONS_PER_SECOND`, `g_network->isSimulated()`, `isGeneralBuggifyEnabled()`, and `reportErrors()`. Helpers include `runTest()`, `makeKey()`, `populateDatabase()`, `populateDatabaseAllActors()`, `txnClient()`, and `workload()`.

## Control Flow
`start()` runs only in simulated, non-general-buggify environments and wraps the main workload in a timeout. The workload populates per-client/per-actor keys in batches, then launches `actorsPerClient` transaction clients. Each client cycles through its keys for 80% of the test duration: get read version, read the value, delay until `txnMinDuration`, increment the value, commit, and count success. On error it retries through `onError()`, obtains a new read version, and classifies failures as expected if they are known recovery errors, large version jumps, or too much real time has passed.

## State and Persistence Behavior
Database state is key/value counters named `txntimeout_c{clientId}_a{actorIdx}_n{nodeIdx}`. Runtime state is counts of total, successful, and failed transactions. The workload disables all failure-injection workloads to keep timeout behavior isolated.

## Dependencies and Integration Points
It integrates with server transaction lifetime knobs, simulation gating, dbInfo recovery state tracing, tester failure-injection controls, and Native API transactions.

## Risks and Edge Cases
`txnsTotal`, `txnsSucceeded`, and `txnsFailed` are plain integers updated by actors on the Flow thread; this is acceptable in actor scheduling but not thread-safe outside it. `std::stoi(val.get().toString())` assumes population succeeded and values are numeric. Classification of expected errors uses best-effort version deltas and elapsed time, so recovery timing can affect pass/fail decisions.

## Test Signals
`check()` fails if any unexpected failures occurred, no transactions succeeded, or success count differs from total attempts. Traces include `TxnTimeoutSetup`, `TxnTimeoutPopulateComplete`, `TxnTimeoutTxnSuccess`, `TxnTimeoutTxnError`, `TxnTimeoutUnexpectedFailure`, `TxnTimeoutExpectedFailure`, and `TxnTimeoutCheckFailure`.
