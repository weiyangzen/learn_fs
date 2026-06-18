# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egverify.c

Implements `egverify(EGpub *pub, EGsig *sig, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The verifier checks `1 <= r < p`, computes `key^r * r^s mod p`, computes `alpha^m mod p`, and compares the two values. It returns `0` on success and `-1` on failure.

Temporary `mpint`s for both sides of the verification equation are allocated and freed locally.
