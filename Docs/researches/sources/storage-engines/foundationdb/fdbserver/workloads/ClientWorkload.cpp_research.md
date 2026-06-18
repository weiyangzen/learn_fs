# sources/storage-engines/foundationdb/fdbserver/workloads/ClientWorkload.cpp

## Purpose
`ClientWorkload.cpp` implements the `ClientWorkload` wrapper, which runs another `TestWorkload` inside a separate simulated client process. It lets tester workloads exercise behavior from distinct process/network/locality contexts while preserving the parent tester interface.

## Important APIs, Types, And Functions
Main helper types are `WorkloadProcessState` and `WorkloadProcess`. Public methods implemented for `ClientWorkload` include the constructor/destructor, `description`, `initialized`, `setup`, `start`, `check`, `getMetrics`, and `getCheckTimeout`. Internals use `g_simulator->newProcess`, `destroyProcess`, `onProcess`, `FlowTransport::createInstance`, `FlowTransport::transport().bind`, `Sim2FileSystem::newFileSystem`, and `Database::createDatabase`.

## Control Flow
`WorkloadProcessState::instance` creates one persistent child process per client id, choosing IPv4 or IPv6 addresses derived from the client id, assigning tester process class/locality, creating a data folder, and binding transport in the child process. `WorkloadProcess` waits for child process initialization, switches to the child process, creates the child workload and database, then switches back. `runActor` switches into the child process to run a child workload actor and switches back to the parent with the result.

## State And Persistence
State includes the simulator child process, child address/name, child data folder, child database handle, child workload reference, and static vector of per-client `WorkloadProcessState*`. The destructor schedules child-process destruction through `impl->destroy`.

## Dependencies And Integration Points
This file integrates deeply with the simulator, process-local Flow transport, simulated filesystem setup, API version selection, workload factories declared in `tester/workloads.h`, and parent/child process switching semantics.

## Risks
Future cancellation must destroy child futures on the child process; `cancelChild` exists for this cross-process lifetime hazard. `ClientWorkload::~ClientWorkload` calls `impl->destroy()` without awaiting its future, relying on actor scheduling to perform cleanup. Static process state is never removed from the vector, so lifecycle is effectively per-client for the simulation. Incorrect process switching before creating/destroying futures can lead to simulator ownership bugs.

## Test Signals
Trace events include `StartingClientWorkloadProcess`, `ClientWorkloadProcessInitialized`, `ClientWorkloadOpenDatabase`, `StartingClientWorkload`, `DeleteWorkloadProcess`, `ShutdownClientForWorkload`, and `DestroyClientWorkload`. Good tests run child workload setup/start/check/metrics and verify no process-context assertions or leaked child actors.
