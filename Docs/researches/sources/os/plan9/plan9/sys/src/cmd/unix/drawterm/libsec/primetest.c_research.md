# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/primetest.c

Standalone primality/DSA-prime test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

`main` installs the mp formatter, constructs known composite and prime examples, checks `probably_prime`, then calls `DSAprimes` and prints generated `q` and `p`. The bottom of the file includes commented example output checked with Maple, including seed, `q`, `p`, and related large values.

This is a diagnostic executable source, not part of the `libsec.a` Makefile object list.
