# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/pmap_clnt.h

Declares compatibility RPC portmapper client remote-call APIs.

It exposes old `pmap_rmtcall` using `struct timeval50` and modern `__pmap_rmtcall50` using `struct timeval`.

This is RPC time ABI compatibility.
