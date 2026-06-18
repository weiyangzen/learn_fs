# sources/storage-engines/foundationdb/contrib/monitoring/CMakeLists.txt

## Purpose
This CMake fragment builds the `actor_flamegraph` monitoring helper executable from `actor_flamegraph.cpp`.

## Important APIs, Types, And Functions
It declares `add_executable(actor_flamegraph actor_flamegraph.cpp)` and links `Threads::Threads` privately.

## Control Flow
The parent CMake project includes this directory, then this fragment contributes one executable target and its thread-library dependency.

## State And Persistence Behavior
No runtime state is defined here. The persistent build artifact is the `actor_flamegraph` executable.

## Dependencies And Integration Points
It depends on the parent project having found or declared `Threads::Threads`. It integrates the standalone parser into FoundationDB contrib monitoring builds.

## Risks And Edge Cases
If the parent CMake file has not called `find_package(Threads)`, target generation can fail. The file does not set C++ standard requirements even though the source uses `unordered_map::contains`, which requires C++20.

## Test Signals
Build configuration should confirm `actor_flamegraph` is generated and linked. A compile test should verify the active C++ standard supports the source.
