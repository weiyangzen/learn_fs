# File Research: sources/os/bsd/netbsd-src/lib/libpthread/compat/pthread.h

## Purpose
Minimal compatibility header for the old `pthread_setname_np` ABI wrapper.

## Main Responsibilities
- Includes `sys/mutex.h` and `pthread_types.h`.
- Declares hidden `__compat_pthread_setname_np`.
- Declares variadic `__pthread_setname_np120`.

## Dependencies
- NetBSD pthread type definitions.
