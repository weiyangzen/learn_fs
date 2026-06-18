# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egencrypt.c

Implements `egencrypt(EGpub *pub, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The intended algorithm reduces the message modulo `p`, selects random ephemeral `k`, computes `gamma = alpha^k mod p`, computes `delta = message * key^k mod p`, and packs `gamma` and `delta` into one `mpint` using a digit-aligned shift.

Important as-read issue: `pm1` is allocated but never initialized to `p-1` before the loop checks `mpcmp(k, pm1) < 0`. Since `pm1` remains zero, the range condition for positive `k` cannot succeed, making this loop appear non-terminating. The rest of the function frees temporaries and returns `out` if the loop is ever exited.
