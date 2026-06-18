# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDReadWrite.cpp

## Purpose
Mock data-distributor workload that runs mock storage servers and a `MockDataDistributor` over a populated `MockGlobalState`, intended to exercise mock DD read/write behavior.

## Important APIs, types, and functions
`MockDDReadWriteWorkload` derives from `MockDDTestWorkload`. It owns a `Reference<DDSharedContext>`, `Reference<DDMockTxnProcessor>`, `MockDataDistributor`, and `ActorCollection`. It uses inherited `populateMgs` and `sharedMgs`.

## Control flow
Setup runs only when enabled, calls the base setup to create `MockGlobalState`, populates mock data, and constructs a `DDMockTxnProcessor`. Start launches all mock servers through `sharedMgs->runAllMockServers()`, starts `dataDistributor.run(ddcx, mock)`, and then delays for `testDuration`. Check currently returns true.

## State and persistence behavior
All state is in the simulated mock DD universe, not FoundationDB user keys. `sharedMgs` contains cluster layout, mock server state, shard sizes, and populated data.

## Dependencies and integration points
Depends on `MockDDTest.h`, `MockDataDistributor`, `DDTxnProcessor` abstractions, `DDSharedContext`, mock servers, and Flow actor collection lifecycle.

## Risks and test signals
Because `check` always returns true and metrics are empty, this workload is mostly a smoke/exercise harness. Risks include actor errors being hidden if not surfaced through `ActorCollection`, incomplete validation of read/write results, and dependency on base mock population. Signal is successful run without actor failure traces.
