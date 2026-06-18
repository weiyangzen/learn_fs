# sources/user-network-fs/mergerfs/src/predictability.h

## Purpose
Provides branch prediction macros for C/C++ code paths.

## Important APIs, Types, and Functions
Defines `likely(x)` and `unlikely(x)` as `__builtin_expect(!!(x), 1 or 0)`.

## Control Flow
The macros annotate conditions for compiler optimization but do not change program semantics.

## State and Persistence Behavior
No state or persistence is involved.

## Dependencies and Integration Points
Used by performance-sensitive inline helpers such as UID/GID switching paths.

## Risks and Edge Cases
Overuse or incorrect prediction can hurt generated code layout. The macros assume a compiler supporting `__builtin_expect`.

## Test Signals
Compile coverage on supported compilers is sufficient; runtime behavior should match unannotated boolean expressions.
