# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/gensafeprime.c

Implements `gensafeprime(mpint *p, mpint *alpha, int n, int accuracy)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function repeatedly generates an `(n-1)`-bit prime `q`, sets `p = 2*q + 1`, and tests `p` for probable primality. Once a safe prime is found, it searches for a generator `alpha` of `Z*_p` by rejecting candidates where `alpha^2 mod p == 1` or `alpha^q mod p == 1`.

Temporary `q` and `b` values are freed before return. The result is stored in caller-owned `p` and `alpha`.
