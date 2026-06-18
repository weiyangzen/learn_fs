# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/nfastrand.c

Defines `nfastrand(ulong n)`, producing an unbiased-ish random value in `[0, n)`. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The function sets `Maxrand` to `2^31 - 1`, aborts if `n > Maxrand`, computes the largest multiple of `n` not exceeding `Maxrand`, and rejects `fastrand()` results outside that range before returning `r % n`.

There is no explicit guard for `n == 0`; callers must avoid zero to prevent modulo/division errors.
