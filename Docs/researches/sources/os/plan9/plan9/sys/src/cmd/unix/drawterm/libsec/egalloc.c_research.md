# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egalloc.c

Defines ElGamal allocation/free helpers: `egpuballoc`, `egpubfree`, `egprivalloc`, `egprivfree`, `egsigalloc`, and `egsigfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use zeroing allocation and `sysfatal` on failure. Free functions release nested `mpint` fields for public keys, private keys, and signatures.

Like `dsaalloc.c`, these free functions do not call `free` on the containing `EGpub`, `EGpriv`, or `EGsig` structs, unlike the RSA free helpers. That ownership pattern should be noted by callers.
