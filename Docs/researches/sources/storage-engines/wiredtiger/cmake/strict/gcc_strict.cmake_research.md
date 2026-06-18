# sources/storage-engines/wiredtiger/cmake/strict/gcc_strict.cmake

## Purpose
`gcc_strict.cmake` selects strict diagnostic flags for GNU C compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_gnu_base_flags(gcc_flags C)`, appends common and C-specific warnings, conditionally enables `-Wunsafe-loop-optimizations` for GCC 4.7, 5, and 6, conditionally suppresses unused inline functions for coverage, and sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
Compiler-version checks gate the noisy unsafe-loop warning. Coverage builds add `-Wno-unused-function`.

## State And Persistence Behavior
The resulting flag list is stored in a CMake variable and applied by target definitions.

## Dependencies And Integration Points
It depends on `CMAKE_C_COMPILER_VERSION`, `CODE_COVERAGE_MEASUREMENT`, and helper-provided GNU base flags. It feeds the library and executable target compile options.

## Risks
Version comparisons use exact major/minor forms and may not catch all older GCC variants. Aggressive warning flags can break builds when code or compiler diagnostics change.

## Test Signals
Compile strict GNU C builds across supported GCC versions and coverage mode; verify expected warning set and no unexpected warning failures.
