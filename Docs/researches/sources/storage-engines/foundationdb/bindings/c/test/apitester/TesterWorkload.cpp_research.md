# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.cpp

## Purpose
Implements generic workload lifecycle, option parsing, task scheduling, transaction wrapper calls, control pipes, progress checks, stats timers, and workload factory lookup.

## Important APIs, types, and functions
`WorkloadConfig::getIntOption/getFloatOption/getBoolOption`, `WorkloadBase::schedule/execTransaction/execOperation/error/scheduledTaskDone`, `WorkloadManager::add/run/workloadDone/openControlPipes/handleStopCommand/handleCheckCommand/confirmProgress`, and `IWorkloadFactory::create/factories`.

## Control flow
The manager initializes and starts all workloads, joins the scheduler, handles optional pipe commands, emits `DONE`, and stops the scheduler when the active workload map empties. `WorkloadBase` increments task counters before work and decrements them after continuations.

## State and persistence behavior
State is in-memory counters, active workload maps, pipe streams, and optional timer. Database writes are delegated to workload transactions.

## Dependencies and integration points
Depends on scheduler, transaction executor, FDB transaction options, `fmt`, and factory registration from workload translation units.

## Risks and test signals
Task-counter imbalance, scheduler stop races, and pipe-thread hangs are key risks. Signals include per-workload success/error logs, `CHECK_OK`, `DONE`, and final failed-workload count.
