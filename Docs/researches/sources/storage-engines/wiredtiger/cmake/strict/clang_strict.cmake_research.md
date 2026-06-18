# sources/storage-engines/wiredtiger/cmake/strict/clang_strict.cmake

## Purpose
`clang_strict.cmake` selects strict diagnostic flags for Clang C compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_clang_base_flags(clang_flags C)`, appends C-specific flags such as `-Weverything`, `-Wjump-misses-init`, `-Wmissing-prototypes`, and several suppressions, then sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
The only conditional disables `-Wunused-function` during code coverage builds because inline functions may not be inlined.

## State And Persistence Behavior
The resulting list is stored in `COMPILER_DIAGNOSTIC_C_FLAGS` for targets configured with strict Clang C diagnostics.

## Dependencies And Integration Points
It is consumed by target definition macros and depends on `CODE_COVERAGE_MEASUREMENT` from `base.cmake`.

## Risks
`-Weverything` is intentionally broad and can break builds when Clang adds new warnings. Suppressions must be maintained as code style or compiler versions change.

## Test Signals
Run Clang strict builds with and without coverage enabled; verify warning flags and successful compilation.
