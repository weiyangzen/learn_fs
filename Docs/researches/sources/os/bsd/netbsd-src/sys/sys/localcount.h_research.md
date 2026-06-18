# File Research: sources/os/bsd/netbsd-src/sys/sys/localcount.h

Kernel-only local reference count API using per-CPU counters plus a total pointer and debug refcount. It declares init, acquire, release, drain, fini, and debug refcount access.

It is used where modules or hooks need to prevent teardown while concurrent users are inside a protected region. Callers provide condition variable and mutex during drain/release coordination. Risks are missed release paths causing unload/drain hangs and incorrect use after finalization.
