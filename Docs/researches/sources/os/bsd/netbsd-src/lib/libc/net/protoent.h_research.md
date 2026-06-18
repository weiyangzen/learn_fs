# File Research: sources/os/bsd/netbsd-src/lib/libc/net/protoent.h

Internal header for protocol database reentrant state. `struct protoent_data` stores the backing `FILE *`, current `struct protoent`, alias vector, stay-open flag, current line buffer, and a dummy compatibility pointer.

It declares the global `_protoent_data`, optional `_protoent_mutex`, and reentrant protocol lookup functions: `getprotoent_r()`, `getprotobyname_r()`, `getprotobynumber_r()`, `setprotoent_r()`, and `endprotoent_r()`.
