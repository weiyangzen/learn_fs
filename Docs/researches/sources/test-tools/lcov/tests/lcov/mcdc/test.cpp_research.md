# sources/test-tools/lcov/tests/lcov/mcdc/test.cpp

## Purpose

`test.cpp` provides the boolean expression under MC/DC test. It can compile either a simple single-condition decision or a compound `a && (b || c)` decision.

## Important APIs, types, and functions

It includes `<stdio.h>` and defines `void test(int a, int b, int c)`. The `SIMPLE` macro selects `if (a)`; otherwise the condition is `if (a && (b || c))`.

## Control flow

`test()` evaluates the selected condition and prints either the formatted expression values or `not..`.

## State and persistence behavior

There is no persistent program state. Instrumentation data from the condition is the state consumed by the MC/DC harness.

## Dependencies and integration points

It is linked with `main.cpp` by both GCC and Clang test paths. Conditional compilation aligns with `mcdc.sh`'s `runGcc` scenarios.

## Risks and test signals

Line and expression layout are part of the test contract. Reformatting the `if` condition or changing macro guards may alter MC/DC records and expected filter behavior.
