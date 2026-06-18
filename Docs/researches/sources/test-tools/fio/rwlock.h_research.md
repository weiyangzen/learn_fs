# sources/test-tools/fio/rwlock.h

Purpose: public type and API for fio read/write locks.

Important APIs/types: defines `FIO_RWLOCK_MAGIC`, `struct fio_rwlock` containing `pthread_rwlock_t lock` and `int magic`, and declares init/read/write/unlock/remove helpers.

Control flow and state: no implementation, but documents that callers manipulate an opaque-ish object allocated by `fio_rwlock_init()`.

Dependencies and integration: includes pthread headers and pairs with `rwlock.c`.

Risks: structure layout is public, so external code could allocate it incorrectly; the implementation expects mmap allocation and magic initialization.

Test signals: compile users and lifecycle tests around the declared API.
