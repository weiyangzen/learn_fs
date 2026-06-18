# sources/storage-engines/foundationdb/fdbserver/workloads/Rollback.cpp

## Purpose
`RollbackWorkload` is a failure injection workload that tries to force transaction log rollback scenarios by partitioning a commit proxy from most tLogs, then either rebooting or clogging the proxy and the remaining tLog interface.

## Important APIs, Types, And Functions
It derives from `FailureInjectionWorkload` and registers both a workload factory and failure-injector factory under `Rollback`. Important options include `meanDelay`, `clogDuration`, `testDuration`, `enableFailures`, and `multiple`. Core actors are `simulateFailure` and `rollbackFailureWorker`.

## Control Flow
Only client 0 is enabled. In simulation, `start` runs `rollbackFailureWorker` until `testDuration`. In multiple mode, failures are scheduled by Poisson delay; otherwise a single failure is delayed within the test window. `simulateFailure` reads current `ServerDBInfo`, chooses a random commit proxy and tLog, clogs proxy links to all other tLogs, waits one third of the clog duration, refreshes system info, and then either reboots the proxy plus clogs the remaining tLog or clogs both interfaces.

## State And Persistence Behavior
The workload does not directly write keys. Its state changes are simulation network partitions and process reboot/clog actions, which affect recovery, logging, and rollback behavior in the cluster.

## Dependencies And Integration Points
It depends on simulator APIs, `MasterInterface`, `ServerDBInfo`, log system configuration, commit proxy interfaces, and `FailureInjectionWorkload` scheduling. It cooperates with the general failure-injection framework through `initFailureInjectionMode`.

## Risks And Edge Cases
The workload skips injection when no tLogs or commit proxies are present, or when a proxy shares IP with a tLog that would be clogged. The member initializer `double meanDelay = 20.0, clogDuration = clogDuration = 3.0` is unusual and worth preserving carefully if edited. Aggressive clogging can interact with unrelated workloads unless they disable failure injection.

## Test Signals
Trace events `AttemptingToTriggerRollback` and `UnableToTriggerRollback` describe whether injection occurred. `check` always returns true; failures surface as cluster/test errors triggered by the injected rollback conditions.
