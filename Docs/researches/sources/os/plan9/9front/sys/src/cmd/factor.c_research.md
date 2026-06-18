# File Research: sources/os/plan9/9front/sys/src/cmd/factor.c

## Purpose
Prints prime factors for numbers supplied as arguments or stdin lines.

## Key Elements
Uses floating-point `double` arithmetic, divides out 2, 3, 5, and 7, then walks candidate factors using a wheel increment table. Prints the original number, each factor indented, and a blank line per input.

## Dependencies
Uses Plan 9 Bio for stdin and libc math functions `sqrt`, `modf`, and `atof`.

## Behavior/Risks
Precision is limited by `double`, so large integers can be misrepresented or factored incorrectly. Stdin mode stops on EOF or non-positive input.
