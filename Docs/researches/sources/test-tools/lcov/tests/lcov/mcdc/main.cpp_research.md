# sources/test-tools/lcov/tests/lcov/mcdc/main.cpp

## Purpose

`main.cpp` drives the MC/DC test by calling `test()` with controlled input combinations. Conditional compilation changes which combinations execute, allowing different MC/DC sensitivity cases.

## Important APIs, types, and functions

It declares `extern void test(int, int, int);` and defines `int main(int ac, char **av)`. Compile-time flags `SENS1` and `SENS2` add calls `test(1,0,0)` and `test(0,1,0)` respectively.

## Control flow

`main()` always calls `test(1,1,0)`, optionally calls the two sensitivity variants, and returns zero.

## State and persistence behavior

The program itself has no persistence. Instrumented builds produce GCC or LLVM coverage data consumed by `mcdc.sh`.

## Dependencies and integration points

It depends on `test.cpp` for the `test()` definition and is compiled by both GCC and Clang paths in `mcdc.sh`.

## Risks and test signals

The exact call combinations determine MC/DC hit/miss counts. Adding or removing calls changes expected downstream `MCDC` records and genhtml behavior.
