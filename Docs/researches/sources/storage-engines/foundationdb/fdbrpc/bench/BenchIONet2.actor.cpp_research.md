# sources/storage-engines/foundationdb/fdbrpc/bench/BenchIONet2.actor.cpp

## Purpose
`BenchIONet2.actor.cpp` benchmarks Flow actor scheduling under mixed task priorities while also performing a small async file write and sync through the Net2 filesystem.

## Important APIs, Types, and Functions
Key functions are actor `increment`, `getRandomTaskPriority`, actor `benchIONet2Actor`, and benchmark wrapper `bench_ionet2`. The benchmark is registered over actor counts from 1 to 65536.

## Control Flow
Each benchmark loop resets a counter, creates `actorCount` `increment` actors with deterministic random priorities, opens `/tmp/__test-benchmark-file__` with atomic create/readwrite flags, writes 4096 zero bytes, syncs the file, and reports items processed. `increment` waits on a zero-delay at the chosen priority, performs CPU work with deterministic random values, prevents optimization, and increments the shared sum.

## State and Persistence Behavior
The benchmark writes a fixed temporary file path under `/tmp` and recreates or overwrites it during iterations. Actor state and random seeds are in-memory. The file may remain after benchmark execution depending on filesystem behavior.

## Dependencies and Integration Points
It depends on Flow actor compiler, `ThreadHelper.actor.h`, `IAsyncFile`, `flow/network.h`, and Google Benchmark. `bench_ionet2` enters the Flow main thread with `onMainThread`.

## Risks and Edge Cases
The fixed temp path can collide with concurrent runs. Opening and syncing a file inside each benchmark iteration mixes scheduler and filesystem costs. `sum` is shared by actors on the Flow thread; if execution assumptions change, it would need synchronization.

## Test Signals
Benchmark throughput across actor counts is the main signal. Successful execution also indicates the benchmark main initialized Net2 filesystem correctly and the Flow scheduler can process the actor burst.
