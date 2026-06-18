# sources/storage-engines/foundationdb/fdbserver/workloads/IDDTxnProcessorApiCorrectness.cpp

## Purpose
Simulation-only parity workload that compares real `DDTxnProcessor` behavior with `DDMockTxnProcessor` behavior for data-distribution movement APIs. It ensures the mock data distributor's transaction processor tracks the real cluster's shard/server mapping after raw and full move-key operations.

## Important APIs, types, and functions
Helper functions `describe`, `compareShardInfo`, and `verifyInitDataEqual` compare `InitialDataDistribution` and `DDShardInfo`. Tester subclasses expose protected `rawStartMovement` and `rawFinishMovement`. `IDDTxnProcessorApiWorkload` owns `DDSharedContext`, real/mock processors, `MockGlobalState`, current boundaries, and counters. Core methods include `readRealInitialDataDistribution`, `getRandomKeys`, `getRandomTeam`, `generateMoveKeysParams`, `testRawMovementApi`, `testMoveKeys`, and `worker`.

## Control flow
Client 0 disables DD mode, reads real initial distribution, initializes mock global state, verifies equality, then runs randomized movement tests until `testDuration`. Each test generates valid key ranges from current shard boundaries and destination teams from real servers, takes move-keys locks, invokes mock and real APIs, handles `movekeys_conflict` by retrying, re-reads real distribution, verifies mock parity, and refreshes mock global state for server changes. It restores DD mode after the run.

## State and persistence behavior
The workload mutates real data-distribution metadata by disabling/enabling DD and issuing move-key operations. Mock state lives in `MockGlobalState` and is rebuilt from real initial distribution. It also updates in-memory shard boundaries after each real read.

## Dependencies and integration points
Depends on DD shared context, `DDTxnProcessor`, `DDMockTxnProcessor`, `MoveKeysParams`, `MockGlobalState`, storage server interfaces, movement locks, shard location metadata mode, and database configuration. It disables `RandomMoveKeys` and Attrition due to direct DD-mode and movement interference.

## Risks and test signals
Risks are destructive movement side effects, race with server recruitment/removal, unsupported multi-region random teams, and strict equality over only fields the mock cares about. Signals are ASSERTs in init equality, destination checks, and post-movement equality plus perf counters `TestRawStart`, `TestRawFinish`, and `TestRawAll`.
