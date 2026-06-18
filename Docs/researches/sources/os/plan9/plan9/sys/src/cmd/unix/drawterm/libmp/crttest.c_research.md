# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crttest.c

Standalone CRT test program.

Key functions:
- `testcrt`: forms a product modulus, tests residue conversion and reconstruction, and prints both values.
- `main`: generates DSA primes repeatedly, runs the CRT test, and reports elapsed seconds.

Dependencies:
- Uses `DSAprimes`, `mpconv`, and libmp arithmetic.
