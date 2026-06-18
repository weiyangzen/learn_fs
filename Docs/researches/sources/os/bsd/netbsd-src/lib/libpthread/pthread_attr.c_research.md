# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_attr.c

This file implements pthread attribute object management and getters/setters for detach state, guard size, inherited scheduling, scheduling parameters, scheduling policy, scope, stack address/size, thread names, create-suspended state, and `pthread_getattr_np`.

The public `pthread_attr_t` stores only magic, flags, and a private pointer. Optional data is lazily allocated by `pthread__attr_init_private`, which initializes defaults from global stack and guard sizes and `SCHED_OTHER`. Destroy frees this private area and poisons the magic. `pthread_attr_get_np` copies live thread state into an attribute object, including flags, stack region, guard size, name argument, and scheduler parameters via `pthread_getschedparam`.

Validation is handled with `pthread__error` checks on magic values. Stack size is checked against `_SC_THREAD_STACK_MIN`; scheduling priorities are passed through `pthread__checkpri`; scheduling policies support `SCHED_OTHER`, `SCHED_FIFO`, and `SCHED_RR`, returning `ENOTSUP` otherwise. `pthread_attr_setname_np` formats into the fixed `PTHREAD_MAX_NAMELEN_NP` buffer and rejects truncation.

Integration points: uses `pthread_int.h` private structures, libc strong aliases for attr init/destroy/detach, and live thread state from `struct __pthread_st`. Main risks are lazy allocation failures, format-string semantics in thread naming, and compatibility of deprecated stack-address APIs.
