# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/CMakeLists.txt

## Purpose
Describes how this source subtree is built, which sources enter the library or executable, and which third-party or sibling CryFS components are linked. This specific file has 25 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
CMake commands used here include `project`, `INCLUDE`, `set`, `add_library`, `target_link_libraries`, `target_enable_style_warnings`, `target_activate_cpp14`, `target_add_boost`, `add_executable`, `set_target_properties`, `install`.

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
