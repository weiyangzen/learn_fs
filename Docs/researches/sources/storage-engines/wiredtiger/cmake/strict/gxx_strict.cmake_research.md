# sources/storage-engines/wiredtiger/cmake/strict/gxx_strict.cmake

## Purpose
`gxx_strict.cmake` selects strict diagnostic flags for GNU C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_gnu_base_flags(gxx_flags CXX)`, optionally appends `-Wno-unused-function` for coverage, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
Coverage mode is the only local conditional, suppressing warnings caused by non-inlined inline functions.

## State And Persistence Behavior
It sets the CMake variable consumed by C++ strict target configuration.

## Dependencies And Integration Points
It depends on `CODE_COVERAGE_MEASUREMENT` and shared GNU strict flag helpers. It affects C++ tests, tools, and model components when strict mode is enabled.

## Risks
The helper carries most warning policy, so C++-specific issues require helper or local updates. Coverage suppression may mask unused helper functions beyond the intended inline-function case.

## Test Signals
Configure GNU C++ strict builds with and without coverage; compile C++ targets and inspect resulting warning flags.
