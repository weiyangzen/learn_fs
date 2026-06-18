# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaencrypt.c

Defines `rsaencrypt(RSApub *rsa, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates `out` if nil and computes `in^ek mod n` with `mpexp`. It returns the output `mpint`.

There is no padding, range checking, or encoding logic in this primitive; callers are responsible for using it safely.
