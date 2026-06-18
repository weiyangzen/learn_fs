# File Research: sources/os/bsd/freebsd-src/sys/sys/_pthreadtypes.h

POSIX pthread public type definitions.

Key elements:
- Forward-declares pthread object structs.
- Defines opaque pointer typedefs for pthreads, attrs, mutexes, condvars, rwlocks, barriers, and spinlocks.
- Defines `pthread_key_t`, `pthread_addr_t`, and start routine type.
- Defines `struct pthread_once`.

Dependencies:
- None explicit.

Research notes:
- Mostly opaque ABI boundary for libc/libpthread.
- `pthread_once_t` is not opaque: it stores state plus a mutex pointer.
