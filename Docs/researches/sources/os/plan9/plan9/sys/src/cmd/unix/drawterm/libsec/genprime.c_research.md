# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genprime.c

Implements `genprime(mpint *p, int n, int accuracy)`, generating an `n`-bit probable prime. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function sizes `p`, fills `(n+7)/8` random bytes with `genrandom`, sets `top`, forces the high bit for exact bit length, masks excess high bits, and forces the low bit to make the candidate odd.

It then increments by two until `probably_prime(p, accuracy)` succeeds. It mutates the caller-supplied `mpint` and does not allocate a return value.
