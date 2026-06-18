# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.h

## Purpose
Shared declaration for mock data-distribution tester workloads. It centralizes common options, mock global state ownership, and population hooks.

## Important APIs, types, and functions
Declares `MockDDTestWorkload : TestWorkload` with public state `enabled`, `simpleConfig`, `testDuration`, `meanDelay`, byte-size/keyspace options, `sharedMgs`, `getRandomRange`, and `setup`. Protected members include `mockDbSize`, `keySize`, strategy controls, and virtual `populateRandomStrategy`, `populateLinearStrategy`, `populateFixedStrategy`, and `populateMgs`.

## Control flow
The header has no executable control flow, but defines the template method shape: derived workloads call base `setup`, optionally override or reuse population methods, and use the populated `sharedMgs`.

## State and persistence behavior
The base contract owns only in-memory mock data-distribution state through `std::shared_ptr<MockGlobalState>`. It does not expose real database persistence behavior.

## Dependencies and integration points
Includes tester workload infrastructure, `DDSharedContext`, `DDTxnProcessor`, move-keys types, and storage server interfaces. It is used by `MockDDReadWrite.cpp` and `MockDDTrackerShardEvaluator.cpp`.

## Risks and test signals
Derived classes depend on base fields remaining consistent with `MockDDTest.cpp` defaults. There are no direct signals in the header; tests come from derived workload checks and mock global state traces.
