# sources/storage-engines/wiredtiger/cmake/strict/cl_strict.cmake

## Purpose
`cl_strict.cmake` selects strict diagnostic flags for MSVC C compilation.

## Important APIs, Types, And Functions
It includes `strict_flags_helpers.cmake`, calls `get_cl_base_flags(cl_flags C)`, and sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
There is no branching beyond helper behavior. The file collects common CL flags and exposes them as the C diagnostic flag list.

## State And Persistence Behavior
It sets a CMake variable consumed later by target definitions, especially `define_wiredtiger_library`.

## Dependencies And Integration Points
It depends on strict flag helper definitions and is selected when strict mode is enabled for MSVC C.

## Risks
Any missing or overly aggressive helper flag affects every strict C target. This file has no local overrides for C-specific suppressions.

## Test Signals
Configure MSVC strict C builds and inspect `COMPILER_DIAGNOSTIC_C_FLAGS` on targets.
