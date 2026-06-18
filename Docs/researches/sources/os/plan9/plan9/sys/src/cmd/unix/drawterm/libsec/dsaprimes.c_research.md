# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprimes.c

Implements `DSAprimes(mpint *q, mpint *p, uchar seed[SHA1dlen])`, following the NIST DSA prime generation algorithm as described in Handbook of Applied Cryptography. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The routine generates a 160-bit `q` using SHA1 over a random seed and incremented seed, forces high/low bits, and tests probable primality. It then constructs 1024-bit `p` candidates so that `q` divides `p-1`, retrying up to 4096 inner attempts before starting over.

Helper functions `Hrand` and `Hincr` operate on 20-byte little-endian seed arrays. `Hrand` uses `fastrand`; primality checks use `probably_prime`. If the caller supplies `seed`, the selected seed is copied out for reproducibility/audit.
