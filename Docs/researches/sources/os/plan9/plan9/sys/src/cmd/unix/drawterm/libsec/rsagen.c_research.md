# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsagen.c

Implements `rsagen(int nlen, int elen, int rounds)`, generating an RSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

A static `genrand` creates a random `elen`-bit public exponent candidate with the top bit set. `rsagen` generates two strong primes, computes `n = p*q` and `phi = (p-1)*(q-1)`, then increments `e` until `gcd(e, phi) == 1` and computes `d = e^-1 mod phi`.

It also precomputes CRT coefficient `c2 = p^-1 mod q` and CRT exponents `kp`, `kq`, then returns an allocated `RSApriv` owning all key components.
