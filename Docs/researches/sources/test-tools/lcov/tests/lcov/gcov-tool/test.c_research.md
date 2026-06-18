# sources/test-tools/lcov/tests/lcov/gcov-tool/test.c

## Purpose

`test.c` is the minimal instrumented C program used by the gcov-tool path-resolution test.

## Important APIs, types, and functions

It defines `int main(int argc, char *argv[])` and returns `0`. Arguments are unused.

## Control flow

The only control flow is process entry and immediate successful return.

## State and persistence behavior

The source has no program state. When compiled with `--coverage` and executed, compiler runtime coverage files are emitted for `path.sh`.

## Dependencies and integration points

It depends only on a C compiler. Its integration value is to generate a simple `.gcno`/`.gcda` pair for LCOV/geninfo capture.

## Risks and test signals

The file intentionally minimizes application logic so failures isolate to compiler, gcov, or LCOV capture behavior.
