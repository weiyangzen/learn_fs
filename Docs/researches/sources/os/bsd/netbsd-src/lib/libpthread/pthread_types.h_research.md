# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_types.h

This public/private ABI header defines pthread object types, object layouts, magic constants, and static initializers. It maps `pthread_t` to `struct __pthread_st *`, defines opaque-looking structs for attributes, mutexes, condition variables, once objects, spinlocks, rwlocks, barriers, and associated attributes, and defines `pthread_key_t` as `int`.

Important layouts include `__pthread_mutex_st` with magic, errorcheck simple lock, optional padding, priority ceiling, volatile owner, volatile waiter list, recursive count, and spare field; `__pthread_cond_st` with magic, unused lock/spare fields, volatile waiter pointer, associated mutex, and private clock pointer; `__pthread_rwlock_st` with reader and writer queues, reader count, owner field, and spare private field; and `__pthread_barrier_st` with waiter queue and generation/count fields.

The header includes C++ accommodations for non-volatile simple-lock typedefs and designated-initializer compatibility macros. It preserves old SA pthread layout compatibility in mutex comments and spare fields.

Integration points: included by `pthread.h` and internal code. Risks are ABI breakage from any layout change, initializer compatibility across C standards and C++, and volatile/padding assumptions across architectures.
