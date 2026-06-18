# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/probably_prime.c

Implements Miller-Rabin probable-prime testing in `probably_prime(mpint *n, int nrep)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function rejects negative candidates with `sysfatal`, handles small/even cases, runs `smallprimetest`, performs a Fermat check `2^n mod n == 2`, then decomposes `n-1` into `q * 2^k` and performs `nrep` Miller-Rabin repetitions.

Witnesses are generated with `mprand(nbits, prng, nil)`, reduced modulo `n-1`, and skipped if `<= 1`. Return value is `1` for probable prime and `0` for composite, with the comment giving error probability below `1/4^nrep`.
