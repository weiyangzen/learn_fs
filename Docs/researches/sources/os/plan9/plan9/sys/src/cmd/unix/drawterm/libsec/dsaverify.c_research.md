# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaverify.c

Implements `dsaverify(DSApub *pub, DSAsig *sig, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The verifier rejects negative or out-of-range `r`/`s`, computes `s^-1 mod q`, then computes `u1 = m*s^-1 mod q` and `u2 = r*s^-1 mod q`. It verifies whether `((alpha^u1 * key^u2) mod p) mod q` equals `r`.

Return convention is `0` for success and `-1` for failure. All temporary `mpint`s are freed through the `out` path.
