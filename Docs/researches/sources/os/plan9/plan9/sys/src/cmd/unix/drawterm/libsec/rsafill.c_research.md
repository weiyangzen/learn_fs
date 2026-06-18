# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsafill.c

Implements `rsafill(mpint *n, mpint *e, mpint *d, mpint *p, mpint *q)`, constructing an `RSApriv` from supplied key parameters. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function verifies `p` and `q` are probably prime, verifies `n == p*q`, and verifies `e*d == 1 mod (p-1)*(q-1)`. On failure it sets `werrstr`, frees local temporaries where needed, and returns nil.

For valid parameters it computes CRT coefficient `c2 = p^-1 mod q`, computes `kp = d mod (p-1)` and `kq = d mod (q-1)`, allocates an `RSApriv`, deep-copies public/private core values, installs CRT fields, and returns the key.
