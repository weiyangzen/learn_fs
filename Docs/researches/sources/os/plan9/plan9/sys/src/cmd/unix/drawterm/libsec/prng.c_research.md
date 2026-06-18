# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/prng.c

Defines `prng(uchar *p, int n)`, a simple buffer filler using libc `rand()`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function iterates over the output buffer and assigns each byte from `rand()`. It is explicitly described as “just use the libc prng”.

This routine is used by `probably_prime.c` for Miller-Rabin witness selection, while cryptographic random generation elsewhere uses `genrandom`.
