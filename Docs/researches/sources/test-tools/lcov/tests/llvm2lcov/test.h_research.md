# sources/test-tools/lcov/tests/llvm2lcov/test.h

## Purpose

`test.h` supplies a small inline helper and macro definitions used by the LLVM coverage fixture.

## Important APIs, types, and functions

It defines `static inline void bar()`, macro `macro_4(expr)` as a ternary that may call `bar()`, and macro `BOOL(x)` as double negation.

## Control flow

`bar()` immediately returns. `macro_4` evaluates `expr` and either does nothing or calls `bar()`. `BOOL` normalizes expressions to boolean values.

## State and persistence behavior

No state is stored. Macro expansions influence coverage records in the including source.

## Dependencies and integration points

It is included by `main.cpp` and indirectly by `llvm2lcov.sh` expectations for macro-related branch and MC/DC entries.

## Risks and test signals

Changing macro structure or line numbers affects LLVM branch and MC/DC output. The header is part of the test fixture's layout-sensitive contract.
