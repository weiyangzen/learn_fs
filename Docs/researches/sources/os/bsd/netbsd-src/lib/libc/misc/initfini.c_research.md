# File Research: sources/os/bsd/netbsd-src/lib/libc/misc/initfini.c

Read completely: 131 lines.

This file implements libc startup initialization in `_libc_init`. It ensures one-time initialization, sets up a static-binary `_dlauxinfo` substitute when possible, initializes stack protector guard, atomic operations, static TLS, threading, and atexit mutexes.

Important interactions: called both from crt0 and global constructor handling, so `libc_initialised` prevents duplicate work. It defines common symbols for `__ps_strings`, `__progname`, and `environ` for compatibility with older binaries.

Security/reliability notes: comments document an ASLR/Emacs undump hazard around `__ps_strings`. Initialization order is security-critical because stack protector setup happens early. `_dlauxinfo` weak-reference behavior differs between static and dynamic binaries.
