# sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.cpp

## Purpose
`pin_threads.cpp` implements named CPU-affinity policies for FUSE read and process threads.

## Important APIs, Types, and Functions
The namespace exposes policy functions `R1L`, `R1P`, `RP1L`, `RP1P`, `R1LP1L`, `R1PP1P`, `RPSL`, `RPSP`, `R1PPSP`, and dispatcher `PinThreads::pin`. Policies use logical CPU vectors or physical core-to-CPU maps from `CPU`.

## Control Flow
Each policy fetches available CPUs/cores, returns if none, and calls `CPU::setaffinity` for read and process pthread ids according to the policy name: one logical CPU, one physical core, read/process together, read/process separated, or spread across CPUs/cores. `pin` ignores empty/`false` type strings and logs a warning for unknown values.

## State and Persistence
No state is stored here. It mutates OS thread affinity masks for the lifetime of the threads.

## Dependencies and Integration Points
It depends on `cpu.hpp` and `syslog.hpp`. `fuse_loop.cpp` calls `PinThreads::pin` after thread-pool creation and before processing continues.

## Risks
Affinity policy names are stringly typed. CPU topology discovery may be unavailable or constrained by cpusets. Some policies reuse the first CPU/core when there are fewer cores than requested, which can concentrate load.

## Test Signals
Test every policy string on single-core, SMT multi-core, and cpuset-limited environments; verify invalid strings warn and `false` is no-op; verify read/process thread ids are pinned as intended.
