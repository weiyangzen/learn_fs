# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egsign.c

Implements `egsign(EGpriv *priv, mpint *m)`, an ElGamal signature routine. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

It computes `p-1`, repeatedly selects an invertible random `k` in the allowed range, computes `r = alpha^k mod p`, and computes `s = k^-1 * (m - secret*r) mod (p-1)`. The inverse is normalized positive with `mpmod`.

It returns an allocated `EGsig` owning `r` and `s`, and frees `pm1`, `k`, and `kinv`. The caller supplies the already-hashed/prepared message as an `mpint`.
