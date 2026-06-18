# sources/storage-engines/wiredtiger/cmake/strict/clxx_strict.cmake

## Purpose
`clxx_strict.cmake` selects strict diagnostic flags for MSVC C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_cl_base_flags(clxx_flags CXX)`, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
There is no branching and no local C++ flag extension beyond helper output.

## State And Persistence Behavior
The file sets a CMake variable that is consumed by strict C++ target setup.

## Dependencies And Integration Points
It depends on `strict_flags_helpers.cmake` and MSVC C++ target configuration.

## Risks
Shared CL helper changes affect both C and C++ strict behavior. Lack of local overrides may make it hard to handle C++-only warnings without editing helpers.

## Test Signals
Configure MSVC C++ strict builds and compile C++ tests/tools that consume `COMPILER_DIAGNOSTIC_CXX_FLAGS`.
