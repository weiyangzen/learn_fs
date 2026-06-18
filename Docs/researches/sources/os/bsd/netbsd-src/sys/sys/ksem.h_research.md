# File Research: sources/os/bsd/netbsd-src/sys/sys/ksem.h

Defines kernel and libc-facing POSIX semaphore internals. In-kernel `ksem_t` tracks global list entry, pshared owner/id/fd, mutex, condition variable, references, value, waiters, name, flags, mode, uid, and gid. Kernel helper declarations cover init/open/wait paths; libc private syscall wrappers are declared under `_LIBC`.

Risks include pshared marker compatibility, reference/lifetime handling, named semaphore permissions, wait interruption/timeouts, and matching libc/kernel opaque handle semantics.
