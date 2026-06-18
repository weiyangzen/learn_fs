# sources/storage-engines/foundationdb/fdbserver/workloads/ClogSingleConnection.cpp

## Purpose
`ClogSingleConnection.cpp` defines a small simulation workload that clogs communication between two random simulator processes after a randomized delay. It is a simple failure-injection workload for one pair of IPs.

## Important APIs, Types, And Functions
The main type is `ClogSingleConnectionWorkload : TestWorkload`, registered by `WorkloadFactory`. It uses `g_simulator->getAllProcesses`, `g_simulator->clogPair`, `delay`, and workload options `minDelay`, `maxDelay`, and `clogDuration`.

## Control Flow
The constructor picks `delaySeconds` uniformly between `minDelay` and `maxDelay` and optionally reads `clogDuration`; if absent, a long default duration of 10000 seconds is used. `start` runs only in simulation on client 0 and maps the delay completion to `clogRandomPair`. That function picks two random processes and clogs their IP pair if they are on different IPs.

## State And Persistence
The only state is simulator network clog state. No database data or system keys are read or written.

## Dependencies And Integration Points
It depends on simulator process metadata and the tester workload framework. It can be combined with other workloads to inject random one-link degradation.

## Risks
Randomly selected processes may include tester or non-server roles; the file does not filter process classes. If both random choices share an IP, no clog is applied. The clog is one directional or pair-level according to simulator `clogPair` semantics and is not explicitly unclogged by this workload.

## Test Signals
There are no explicit trace events in `clogRandomPair`. The observable signal is simulator network behavior and downstream workload/recovery traces. `check` always returns true.
