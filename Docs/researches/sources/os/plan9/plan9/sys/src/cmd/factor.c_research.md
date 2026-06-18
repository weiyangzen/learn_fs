# File Research: sources/os/plan9/plan9/sys/src/cmd/factor.c

Simple integer factorization utility implemented with floating-point arithmetic.

Key behavior:
- Factors command-line operands or newline-separated stdin values.
- Prints the original number, then one factor per indented line, then a blank line.
- Removes factors 2, 3, 5, and 7 first.
- Uses a wheel increment table to test candidate divisors after small primes.

Important implementation details:
- Inputs are parsed with `atof()` and stored as `double`.
- Divisibility is tested with `modf(n/d, &quot) == 0`.
- Trial division stops once the divisor exceeds `sqrt(n)+1`.

Risks and invariants:
- Precision is limited by `double`, so very large integers may factor incorrectly.
- The utility is oriented toward traditional Plan 9 command-line use, not arbitrary precision factoring.
