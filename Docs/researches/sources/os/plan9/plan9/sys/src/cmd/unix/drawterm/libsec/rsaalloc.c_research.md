# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaalloc.c

Defines RSA allocation/free helpers: `rsapuballoc`, `rsapubfree`, `rsaprivalloc`, and `rsaprivfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use `mallocz` and terminate with `sysfatal` on allocation failure. `rsapubfree` frees public exponent and modulus, then frees the struct. `rsaprivfree` frees public fields, private exponent, prime factors, CRT exponents, CRT coefficient, and the struct.

This file has complete container ownership cleanup, unlike the DSA/ElGamal free helpers nearby.
