# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_specific.c

This file implements the fast public accessors for pthread thread-specific data and current CPU reporting. `pthread_setspecific` falls back to libc stubs when active, otherwise gets `pthread__self` and delegates to `pthread__add_specific`. `pthread_getspecific` directly indexes the current thread's `pt_specific[key].pts_value`, making reads very cheap and unsynchronized. `pthread_curcpu_np` reads the current CPU from the thread's `lwpctl` area and asserts it is valid.

It also overrides `setcontext` through `pthread_setcontext` to preserve the pthread private pointer: when `_UC_TLSBASE` is set in the incoming context, it copies the context, clears that flag, and calls `_sys_setcontext`.

Integration points: pairs with key allocation/destruction in `pthread_tsd.c`, libc strong aliases, and machine TLS/LWP control state. Risks are unchecked key indexing in `pthread_getspecific`, relying on valid key use by callers, and architecture-specific context/TLS preservation.
