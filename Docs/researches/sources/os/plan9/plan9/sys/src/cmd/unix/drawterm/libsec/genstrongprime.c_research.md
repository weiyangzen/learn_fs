# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genstrongprime.c

Implements `genstrongprime(mpint *p, int n, int accuracy)` using Gordon’s strong-prime algorithm. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function enforces a minimum size of 64 bits, generates auxiliary primes `s` and `t`, finds a prime `r = 2*i*t + 1`, computes an initial `p0 = 2*(s^(r-2) mod r)*s - 1`, then searches by adding multiples of `2*r*s` until `p` passes `probably_prime`.

It allocates and frees temporary `mpint`s for `s`, `t`, `r`, and `i`, mutating the caller-supplied `p` with the final strong prime.
