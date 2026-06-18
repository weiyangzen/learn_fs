# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sethostent.c

Host database control and dispatch implementation. It provides `sethostent()`, `endhostent()`, and related reentrant helpers that coordinate resolver state, `/etc/hosts` file state, and name-service-switch dispatch for host lookups.

The implementation is part of the libc host lookup stack declared by `hostent.h`, connecting public host APIs to backend sources such as files, DNS, and optional NIS through `nsdispatch()`. State is serialized for the non-reentrant public interfaces and kept in caller-supplied buffers for the `_r` variants.
