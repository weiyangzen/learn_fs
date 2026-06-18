# sources/distributed-fs/xrootd/src/XrdRmc/CMakeLists.txt

## Purpose

This CMake fragment adds the RMC memory-cache implementation sources and headers to the `XrdUtils` target.

## Important APIs, Types, And Functions

- `target_sources(XrdUtils PRIVATE ...)` registers `XrdRmc.cc`, `XrdRmcData.cc`, `XrdRmcReal.cc`, and their headers plus `XrdRmcSlot.hh`.

## Control Flow

CMake evaluates this fragment during the main build and compiles RMC directly into `XrdUtils`; it does not create a separate plugin or library target.

## State And Persistence

The file has no runtime state. Build-state effect is that RMC symbols become part of `XrdUtils`.

## Dependencies And Integration Points

It depends on a parent build defining `XrdUtils`. RMC then integrates with any component linking `XrdUtils` and using `XrdOucCache`.

## Risks And Edge Cases

- Because headers are listed as private target sources, install/export behavior depends on the broader project rules.
- Any source added to RMC must be added here or it will not compile into `XrdUtils`.

## Test Signals

Build signal is successful compilation of `XrdUtils` with RMC enabled. Link tests should verify `XrdRmc::Create` is available to consumers.
