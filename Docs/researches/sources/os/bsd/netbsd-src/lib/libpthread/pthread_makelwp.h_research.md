# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_makelwp.h

This private header declares `pthread__makelwp`, the helper used to create a new NetBSD LWP for a pthread. The function accepts a start routine, argument, private pointer, stack base and size, LWP creation flags, and an output LWP id. It includes `<lwp.h>`, public pthread definitions for `PTHREAD_HIDE`, and `pthread_int.h`.

Integration points: the implementation is in `pthread_makelwp_netbsd.c` and is used by thread creation code outside this listed group. Its interface isolates machine/context setup and `_lwp_create` details from higher-level pthread creation logic.

Risks are ABI expectations around `ucontext_t`, stack pointer direction, private TLS/thread pointer passing, and LWP creation flag semantics.
