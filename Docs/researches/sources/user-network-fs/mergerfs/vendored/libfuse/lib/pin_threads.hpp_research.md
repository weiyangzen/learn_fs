# sources/user-network-fs/mergerfs/vendored/libfuse/lib/pin_threads.hpp

## Purpose
`pin_threads.hpp` declares the CPU-affinity policy API for FUSE read and process worker threads.

## Important APIs, Types, and Functions
It declares the individual policy functions and the dispatcher `pin(const CPU::ThreadIdVec&, const CPU::ThreadIdVec&, const std::string&)` in namespace `PinThreads`.

## Control Flow
The header has no runtime flow. Callers pass read-thread ids, process-thread ids, and a policy string to the implementation.

## State and Persistence
No state is declared. Affinity changes are applied by the implementation to live pthreads.

## Dependencies and Integration Points
It includes `cpu.hpp` for thread id vector types and `<string>`. `fuse_loop.cpp` is the primary caller.

## Risks
Public policy declarations must stay synchronized with the dispatcher implementation. Adding a policy in the header without dispatcher support will compile but be unreachable through config.

## Test Signals
Build tests should catch signature drift. Config tests should verify every documented policy string maps to a declared implementation.
