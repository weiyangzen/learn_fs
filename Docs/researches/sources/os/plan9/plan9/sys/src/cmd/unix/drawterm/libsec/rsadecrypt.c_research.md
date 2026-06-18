# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsadecrypt.c

Implements `rsadecrypt(RSApriv *rsa, mpint *in, mpint *out)` using Garner’s CRT algorithm. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The input is reduced modulo `p` and `q`, exponentiated with precomputed `kp` and `kq`, then recombined as `v1 + p * ((v2 - v1) * c2 mod q)`, where `c2` is the inverse of `p` modulo `q`.

The function allocates `out` if nil, uses two temporary `mpint`s, frees them, and returns the decrypted value.
