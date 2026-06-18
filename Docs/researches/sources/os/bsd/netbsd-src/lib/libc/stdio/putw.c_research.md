# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putw.c

Implements historical `putw(int, FILE *)`. It writes the raw `int` bytes through `__sfvwrite()` using a single vector under the stream lock.

Like `getw()`, this is host representation dependent and primarily compatibility-oriented.
