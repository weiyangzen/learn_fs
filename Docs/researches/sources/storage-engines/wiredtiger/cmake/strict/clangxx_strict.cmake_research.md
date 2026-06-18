# sources/storage-engines/wiredtiger/cmake/strict/clangxx_strict.cmake

## Purpose
`clangxx_strict.cmake` selects strict diagnostic flags for Clang C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_clang_base_flags(clangxx_flags CXX)`, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
There are no local C++-specific additions in this file; helper-provided flags define the behavior.

## State And Persistence Behavior
It sets the CMake variable used by C++ targets that opt into strict diagnostics.

## Dependencies And Integration Points
It is used by the broader strict-mode build setup and depends on helper flag definitions.

## Risks
Because there are no local overrides, all C++ warning policy comes from the shared helper. C++ targets may need future targeted suppressions as Clang evolves.

## Test Signals
Configure Clang C++ strict builds and verify C++ unit/model/cppsuite targets compile with the helper flags.
