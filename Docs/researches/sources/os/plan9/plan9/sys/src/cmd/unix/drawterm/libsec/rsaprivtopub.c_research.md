# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaprivtopub.c

Defines `rsaprivtopub(RSApriv *priv)`, deep-copying an RSA public key from a private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `RSApub`, copies modulus `n` and public exponent `ek`, and returns the new key. The returned key owns its `mpint` copies and should be released with `rsapubfree`.

No validation is performed.
