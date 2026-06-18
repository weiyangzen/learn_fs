# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/lrand.c

Thread-safe pseudo-random number generator.

Key responsibilities:
- Implements the D. P. Mitchell and J. A. Reeds lagged Fibonacci-style generator.
- `isrand()` initializes state using Park-Miller parameters.
- `srand()` seeds under a lock.
- `lrand()` lazily initializes if needed, advances tap/feed pointers, stores the new value, and returns a 31-bit positive `long`.

Research notes:
- Uses a global `Lock lk`, so calls are serialized.
- `NORM` is defined but unused in this file.
