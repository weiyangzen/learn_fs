# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprivtopub.c

Defines `dsaprivtopub(DSApriv *priv)`, copying the public part of a DSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates a `DSApub`, then deep-copies `p`, `q`, `alpha`, and `key` from `priv->pub`. The returned public key owns its copies.

No validation is performed; the function assumes `priv` and all public members are initialized.
