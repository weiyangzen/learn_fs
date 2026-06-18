# sources/storage-engines/foundationdb/fdbserver/workloads/TriggerRecovery.cpp

## Purpose
`TriggerRecoveryLoopWorkload` repeatedly forces cluster recoveries by either changing resolver configuration or rebooting all workers, then restores the original resolver count. It is a recovery stress workload.

## Important APIs, Types, and Functions
The workload uses `getDatabaseConfiguration()`, `ManagementAPI::changeConfig()`, `ConfigureAutoResult`, `ReadYourWritesTransaction`, `ClientWorkerInterface`, worker interface system keys, `RebootRequest`, and self-conflicting system-immediate transactions in `returnIfClusterRecovered()`.

## Control Flow
Client 0 setup records the original desired resolver count. `_start()` waits `startTime`, then loops `numRecoveries` times. Each iteration either calls `killAll()` with probability `killAllProportion` or toggles the resolver count between original and original+1. Between recoveries it waits `delayBetweenRecoveries` and confirms the cluster can commit a self-conflicting transaction. A catch block suppresses errors so that resolver count can be reset to the original value at the end.

## State and Persistence Behavior
Persistent configuration state is the resolver count changed through the management API. Operational state changes include worker reboot requests. The workload reads system worker interfaces and may write legacy reboot keys for old API versions. It attempts to restore resolver count even after an error.

## Dependencies and Integration Points
It integrates with management configuration APIs, status/system worker metadata, RYW transactions, and worker reboot interfaces. It is designed for simulation and recovery tests where external workloads validate cluster survival.

## Risks and Edge Cases
If `setOriginalNumOfResolvers()` fails or does not run, optional resolver fields are required later and can assert. `killAll()` reboots every worker interface, including potentially critical roles, so progress depends on the simulation recovering. The catch block in `_start()` hides the original failure reason except through trace logs.

## Test Signals
Trace events include `TriggerRecoveryLoopSetup`, `TriggerRecoveryLoop_ChangeResolverConfigSuccess`, `TriggerRecoveryLoop_ChangeResolverConfigFailed`, `TriggerRecoveryLoop_AttempedKillAll`, `TriggerRecoveryLoop_AttempedRecovery`, and cluster version logs. `check()` always returns true.
