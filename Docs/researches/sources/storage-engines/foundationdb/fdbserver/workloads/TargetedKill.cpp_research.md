# sources/storage-engines/foundationdb/fdbserver/workloads/TargetedKill.cpp

## Purpose
`TargetedKillWorkload` kills or suspends a selected process or machine role after a delay. It is a deterministic fault-injection workload for master, proxy, tlog, storage server, and cluster-controller failure cases.

## Important APIs, Types, and Functions
The workload uses `getStorageServers()`, `getWorkers()`, `WorkerDetails`, `StorageServerInterface`, `CommitProxyInterface`, `GrvProxyInterface`, `TLogInterface`, simulator `killInterface()`, and worker `clientInterface.reboot.send(RebootRequest)`. Key methods are `assassin()` and `killEndpoint()`.

## Control Flow
Only client 0 runs. After `killAt`, `assassin()` retrieves storage servers and workers, selects an address based on `machineToKill`, avoids the cluster-controller address where possible for proxy/tlog/storage roles, and calls `killEndpoint()`. For storage roles it can kill `numKillStorages` servers in a loop. `killEndpoint()` uses simulator instant kill when running under the simulator network, otherwise sends reboot requests to matching workers and optionally all processes on the same IP.

## State and Persistence Behavior
The workload does not modify database data. It modifies cluster process state by killing or suspending worker endpoints. Configuration fields determine whether the target reboots after `suspendDuration` or is effectively suspended indefinitely.

## Dependencies and Integration Points
It depends on live `dbInfo`, worker/interface discovery, core role interfaces, quiet-database state, and the simulator. It integrates with the tester fault-injection ecosystem as a named workload.

## Risks and Edge Cases
Role selection assumes non-empty role lists; random selection over empty storage/proxy/tlog lists would fail. Non-simulator mode matches by master endpoint primary address and optionally IP, skipping tester processes for whole-machine kills. Unknown `machineToKill` leaves `machine` default-constructed before `killEndpoint()`. `check()` is always true, so cluster recovery is validated externally.

## Test Signals
Trace events include `IsolatedMark`, `WorkerKill`, `WorkersKilledAtEndpoint`, and `WorkerNotFoundAtEndpoint`. The workload's own success condition is simply completing the kill action.
