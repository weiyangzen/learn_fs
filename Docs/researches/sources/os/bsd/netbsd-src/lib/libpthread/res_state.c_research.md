# File Research: sources/os/bsd/netbsd-src/lib/libpthread/res_state.c

This file provides thread-safe resolver state handling for multi-threaded programs. It maintains a global singly-linked free list of `_res_st` objects protected by `res_mtx`. `__res_get_state` checks out an existing resolver state or allocates a new one, initializes it with `res_ninit` when needed, and returns a `res_state`. Allocation or initialization failures set `h_errno = NETDB_INTERNAL`.

`__res_put_state` casts the state back to `_res_st` and returns it to the free list. `__res_state`, which corresponds to global `_res` macro usage, deliberately writes an error message to stderr and aborts because shared `_res` is not supported in multi-threaded programs.

Integration points: uses pthread mutexes, resolver library structures, and NetBSD resolver APIs. Risks are pooled state lifetime management, no cleanup of the global free list in this file, and hard abort for incompatible global resolver state access.
