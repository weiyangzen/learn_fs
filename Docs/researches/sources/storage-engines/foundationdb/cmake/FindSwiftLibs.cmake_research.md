# sources/storage-engines/foundationdb/cmake/FindSwiftLibs.cmake

## Purpose
Provides helper functions to query Swift runtime library search and resource paths from the active Swift compiler.

## Important APIs, Types, and Functions
Defines `swift_get_linker_search_paths(var)` and `swift_get_resource_path(var)`.

## Control Flow and Integration
Each function runs `${CMAKE_Swift_COMPILER} -print-target-info` with Apple SDK flags when needed, parses JSON path fields, and returns path lists to the caller. fdbserver Swift integration uses these to link Swift runtime libraries and module maps.

## State and Persistence
Depends on Swift compiler JSON output, CMake `string(JSON)`, and `CMAKE_OSX_SYSROOT` on Apple.

## Dependencies
No persisted files; results are parent-scope variables.

## Risks and Test Signals
Risks include malformed JSON, empty path arrays, cross-compile target mismatch, and duplicated code between helpers. Test signals are Swift-enabled fdbserver link and generated module-map/header flows.
