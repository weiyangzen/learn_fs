# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent.c

Read completely: 80 lines.

This file implements the non-reentrant protocol database entry points: `setprotoent`, `endprotoent`, and `getprotoent`.

It defines the global `_protoent_mutex` and `_protoent_data`, then wraps the reentrant protocol database functions under the mutex.

Security/reliability notes: mutexing serializes access, but returned `protoent` data is global shared state.
