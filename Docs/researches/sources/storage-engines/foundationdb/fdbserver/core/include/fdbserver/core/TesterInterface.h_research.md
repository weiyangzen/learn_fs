# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TesterInterface.h

## Purpose
`TesterInterface.h` declares the RPC contracts used by simulation/tester workers to recruit and drive workloads.

## Important APIs, Types, And Functions
`CheckReply` wraps a boolean. `WorkloadInterface` exposes setup, start, check, metrics, and stop request streams. `WorkloadRequest` carries workload title, timeout, database ping delay, shared random number, database usage flag, compound workload option lists, ranges to check, client index/count, failure workload controls, and a reply with `WorkloadInterface`. `TesterInterface` exposes a recruitment stream.

## Control Flow
The tester recruits workload actors on clients, sends setup/start/check/metrics/stop messages through the returned workload interface, and coordinates multiple clients by shared random number and client counts.

## State And Persistence Behavior
The interface is transient test control state. Workloads may mutate the database, but the request metadata itself is not persistent.

## Dependencies And Integration Points
It depends on RPC, performance metrics, Native API, arenas, and FDB key/value option encoding. It integrates with simulation test workloads and worker recruitment.

## Risks And Edge Cases
Arena-backed `StringRef` and option vectors require correct lifetime management. Failure-workload disabling and `rangesToCheck` must serialize consistently across testers.

## Test Signals
Simulation test harnesses validate recruitment, workload lifecycle ordering, metrics collection, check replies, multi-client option propagation, and failure-injection toggles.
