# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/eggen.c

Implements `eggen(int nlen, int rounds)`, generating an ElGamal private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `EGpriv`, initializes public `p`, `alpha`, `key`, and private `secret`, then calls `gensafeprime` to produce a safe prime modulus and generator. It chooses a random `nlen-1` bit secret and computes `key = alpha^secret mod p`.

Returned ownership is held by the allocated `EGpriv`; callers free nested fields through `egprivfree`.
