# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genrandom.c

Implements `genrandom(uchar *p, int n)` using a DES3-backed ANSI X9.17-style generator. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

A static `State` holds a `QLock`, seeded flag, 64-bit seed, and `DES3state`. `X917init` builds a 3DES key from repeated `truerand()` calls, initializes the DES3 state, warms the generator with 128 bytes, and marks it seeded.

`X917` encrypts the current `nsec()` timestamp to derive `I`, then repeatedly computes output blocks from `E_k(I ^ seed)` and updates `seed` with `E_k(output ^ I)`. `genrandom` serializes access with `qlock`/`qunlock`, initializes once, and fills the requested buffer.
