# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/integral.c

Integral layout helper.

Key behavior:
- `setintegral()` constructs the integral sign box from tuned definition text.
- `integral()` composes an integral sign with optional lower and upper limits using `fromto()`.

Filesystem relevance:
- Typesetting layout only.
