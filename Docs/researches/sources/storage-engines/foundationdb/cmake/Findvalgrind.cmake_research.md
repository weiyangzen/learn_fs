# sources/storage-engines/foundationdb/cmake/Findvalgrind.cmake

## Purpose
Finds Valgrind headers and executable for valgrind-enabled builds.

## Important APIs, Types, and Functions
Searches include dirs for Valgrind headers, finds `valgrind_EXECUTABLE`, sets `valgrind_INCLUDE_DIRS`, `valgrind_FOUND`, and related variables.

## Control Flow and Integration
`FDBComponents.cmake` uses this module when `USE_VALGRIND` is enabled and creates an interface target carrying include dirs.

## State and Persistence
Depends on Valgrind development headers and binary.

## Dependencies
No generated state; discovery variables persist.

## Risks and Test Signals
Risks include enabling Valgrind compile definitions without matching runtime environment. Test signals are configure success under `USE_VALGRIND` and valgrind CTest runs.
