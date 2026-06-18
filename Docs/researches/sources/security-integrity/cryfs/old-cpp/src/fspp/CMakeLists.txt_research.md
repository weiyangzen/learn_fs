# sources/security-integrity/cryfs/old-cpp/src/fspp/CMakeLists.txt

## Purpose
Describes how this source subtree is built, which sources enter the library or executable, and which third-party or sibling CryFS components are linked. This specific file has 3 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
CMake commands used here include `add_subdirectory`.

## Control Flow
CMake control is declarative: sources are grouped into targets, include directories are exposed, and link dependencies connect this subtree to Boost, Crypto++, fspp, blockstore, and CryFS components.

## State and Persistence Behavior
No runtime state is stored. The build graph persists only as generated build-system metadata.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Build scripts can silently omit files or platform-specific sources; target/link changes should be validated on Linux and Windows configurations.

## Test Signals
Validate by configuring and building the old-cpp tree on supported platforms, including test targets and platform-specific source selection.
