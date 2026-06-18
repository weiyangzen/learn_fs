# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimetest.c

Implements trial division by a static table of small primes in `smallprimetest(mpint *p)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The file embeds a large static `ulong smallprimes[]` list ending at `104729`. Static helper `divides(mpint *dividend, ulong divisor)` performs long division over `mpint` limbs using `mpdigdiv` to determine whether the divisor divides the candidate.

`smallprimetest` iterates the table, stops early when the candidate is a single limb not larger than the current small prime, and returns `-1` if divisible by a small prime or `0` otherwise. It is used as a fast composite filter before Miller-Rabin in `probably_prime.c`.
