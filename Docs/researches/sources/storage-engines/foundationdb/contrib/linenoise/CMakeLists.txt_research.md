# sources/storage-engines/foundationdb/contrib/linenoise/CMakeLists.txt

## Purpose
This CMake file builds the vendored `linenoise` terminal line-editing library.

## Important APIs, Types, And Functions
It declares `add_library(linenoise STATIC linenoise.c)`, exposes the local `include` directory publicly, and disables clang-tidy for the target.

## Control Flow
CMake creates a static library from `linenoise.c`. Any target linking to `linenoise` receives `include/linenoise` headers.

## State And Persistence Behavior
Only build graph state is affected. Runtime terminal and history state live in `linenoise.c`.

## Dependencies And Integration Points
The target integrates vendored BSD-licensed source with the parent FoundationDB CMake build. Disabling clang-tidy avoids enforcing project style on third-party code.

## Risks And Edge Cases
The target is Unix-oriented because `linenoise.c` uses termios and POSIX APIs. Build portability depends on parent platform guards.

## Test Signals
Build tests should verify the static target compiles and headers can be included by FoundationDB CLI components that need line editing.
