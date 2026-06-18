# sources/storage-engines/foundationdb/fdbserver/workloads/SuspendProcesses.cpp

## Purpose
`SuspendProcessesWorkload` selects worker processes by address prefix and sends reboot requests that suspend them for a configured duration. It is a targeted fault-injection workload for process suspension scenarios.

## Important APIs, Types, and Functions
The workload uses `ReadYourWritesTransaction`, system key range `\xff\xff/worker_interfaces/`, `ClientWorkerInterface`, `RebootRequest(false, false, suspendTimeDuration)`, `BinaryReader::fromStringRef()`, and `boost::starts_with()`.

## Control Flow
Only client 0 runs `_start()`. It waits `waitTimeDuration`, reads all worker interface entries with `ACCESS_SYSTEM_KEYS` and `LOCK_AWARE`, strips `/worker_interfaces/` and optional `:tls`, matches each address against `prefixesSuspendProcesses`, records selected serialized interfaces, and sends reboot requests to each selected worker's client interface.

## State and Persistence Behavior
The workload reads system worker-interface metadata but does not persist database user data. Its effect is operational state: selected workers are suspended/rebooted by request for `suspendTimeDuration`.

## Dependencies and Integration Points
It integrates with FDB system keys, serialized worker interfaces, the tester framework, and simulation or real worker reboot channels. It depends on address-string prefixes supplied by test configuration.

## Risks and Edge Cases
If prefixes are empty, no workers are selected and the workload still passes. Prefix matching is string-based and may be brittle with IPv6, TLS suffixes, or port formatting. It assumes the worker interface range is small enough for `CLIENT_KNOBS->TOO_MANY`.

## Test Signals
Selected processes are logged via `SuspendProcessSelectedProcess`. `check()` always returns true, so validation comes from surrounding simulation resilience checks.
