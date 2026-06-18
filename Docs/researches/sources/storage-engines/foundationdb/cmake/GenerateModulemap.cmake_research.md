# sources/storage-engines/foundationdb/cmake/GenerateModulemap.cmake

## Purpose
Generates Swift module maps and VFS overlays for C++ headers of a CMake target.

## Important APIs, Types, and Functions
Defines `generate_modulemap(out module target OMIT ... HEADERS ...)`.

## Control Flow and Integration
The function reads target `HEADER_FILES` unless explicit headers are provided, builds `header` entries while omitting requested names, detects generated vs source headers, and configures `empty.modulemap` and `headeroverlay.yaml` templates.

## State and Persistence
Depends on target header properties set by `FlowCommands.cmake`, CMake path operations, and Swift build support templates.

## Dependencies
Generated `module.modulemap` and `headeroverlay.yaml` persist under the requested output directory.

## Risks and Test Signals
Risks include heuristic directory handling for only a few nesting levels and source/generated path overlay mismatches. Test signals are Swift compilation importing the generated module.
