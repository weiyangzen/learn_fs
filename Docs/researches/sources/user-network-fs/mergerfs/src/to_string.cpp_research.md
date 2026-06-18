# sources/user-network-fs/mergerfs/src/to_string.cpp

## Purpose
Implements numeric `to_string` helpers for fixed-width integer types.

## Important APIs, Types, and Functions
Defines `str::to_string()` overloads for `u64`, `u32`, `u16`, `s64`, `s32`, and `s16`, forwarding to `std::to_string()`.

## Control Flow
Each overload returns immediately from the standard conversion.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Complements `to_string.hpp` and avoids ambiguity around project typedefs from `base_types.h`.

## Risks and Edge Cases
Formatting is base-10 only and locale-independent like `std::to_string` for integers. Missing overloads for other types may select unintended standard overloads.

## Test Signals
Test min/max signed and unsigned values and compile-time overload resolution.
