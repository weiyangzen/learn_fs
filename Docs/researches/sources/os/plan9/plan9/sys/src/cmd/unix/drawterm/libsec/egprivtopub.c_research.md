# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egprivtopub.c

Defines `egprivtopub(EGpriv *priv)`, deep-copying public ElGamal fields. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `EGpub`, then copies `p`, `alpha`, and `key` from the private key’s embedded public structure. It returns nil only if allocation unexpectedly returns nil, though `egpuballoc` itself calls `sysfatal` on failure.

No validation is done; initialized input is assumed.
