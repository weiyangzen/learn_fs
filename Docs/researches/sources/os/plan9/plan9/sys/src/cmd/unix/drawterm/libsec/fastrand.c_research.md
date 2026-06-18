# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/fastrand.c

Defines `fastrand(void)`, a convenience random `ulong` generator. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The function fills a local `ulong x` with `genrandom` and returns it. The file comment describes this as using the X9.17 random number generator, faster than `truerand` but less random.

The implementation delegates all state and entropy handling to `genrandom.c`.
