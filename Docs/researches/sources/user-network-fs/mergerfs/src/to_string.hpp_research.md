# sources/user-network-fs/mergerfs/src/to_string.hpp

## Purpose
Declares project-specific numeric string conversion overloads.

## Important APIs, Types, and Functions
The `str` namespace declares `to_string` overloads for `u64`, `u32`, `u16`, `s64`, `s32`, and `s16`.

## Control Flow
Declaration-only header.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Includes `base_types.h` and is used by config/control formatting code.

## Risks and Edge Cases
Overload sets must match definitions in `to_string.cpp` to avoid link failures.

## Test Signals
Compile/link tests for every declared overload and formatting comparisons with expected decimal strings.
