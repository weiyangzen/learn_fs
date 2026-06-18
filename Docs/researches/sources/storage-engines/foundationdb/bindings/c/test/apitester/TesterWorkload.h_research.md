# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.h

## Purpose
Declares workload interfaces, shared base behavior, workload manager, and registry-based factory support for the C API tester.

## Important APIs, types, and functions
`IWorkloadControlIfc`, `IWorkload`, `WorkloadConfig`, `WorkloadBase`, `WorkloadManager`, `IWorkloadFactory`, and `WorkloadFactory<T>` form the workload framework.

## Control flow
Derived workloads schedule tasks and execute transactions through `WorkloadBase`. `WorkloadManager` starts workloads, tracks active entries, handles control commands, and stops the scheduler on completion.

## State and persistence behavior
Declared state includes atomics for task/error/transaction counts, workload failure/in-progress flags, active-workload map, control pipes, and stats timer. FDB persistence happens inside workload transactions.

## Dependencies and integration points
Depends on `TesterTransactionExecutor`, `TesterScheduler`, `TesterUtil`, atomics, mutexes, threads, and streams. TOML workload names must match registered factories.

## Risks and test signals
Unregistered names, self-blocking workloads with insufficient scheduler threads, and missed progress acknowledgments are the main risks. Workload success/failure logs and control-pipe responses are signals.
