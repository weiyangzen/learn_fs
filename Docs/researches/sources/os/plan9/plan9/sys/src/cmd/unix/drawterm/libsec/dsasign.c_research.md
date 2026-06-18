# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsasign.c

Implements `dsasign(DSApriv *priv, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The signer computes `q-1`, repeatedly chooses a random `k` in the DSA range with an inverse modulo `q`, makes the inverse positive, computes `r = (alpha^k mod p) mod q`, and computes `s = k^-1 * (m + secret*r) mod q`.

It returns a newly allocated `DSAsig` owning `r` and `s`, while freeing temporary `qm1`, `k`, and `kinv`. The message `m` is treated as an `mpint` already prepared by the caller, not hashed inside this function.
