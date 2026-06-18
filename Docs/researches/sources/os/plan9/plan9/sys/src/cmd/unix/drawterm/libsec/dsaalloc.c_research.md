# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaalloc.c

Defines DSA allocation/free helpers: `dsapuballoc`, `dsapubfree`, `dsaprivalloc`, `dsaprivfree`, `dsasigalloc`, and `dsasigfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use `mallocz(sizeof(*obj), 1)` and call `sysfatal` on allocation failure. Free helpers release nested `mpint` members for public keys, private keys, and signatures.

Notable ownership detail: unlike the RSA and ElGamal free helpers in nearby files, these DSA free functions free nested `mpint`s but do not call `free(dsa)` on the containing struct. This may be intentional legacy convention or a leak/inconsistency relative to the other key types.
