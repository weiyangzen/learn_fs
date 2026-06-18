# sources/test-tools/fio/rwlock.c

Purpose: fio wrapper around a process-shared pthread read/write lock allocated in shared memory.

Important APIs/functions: `fio_rwlock_init()`, `fio_rwlock_read()`, `fio_rwlock_write()`, `fio_rwlock_unlock()`, and `fio_rwlock_remove()`.

Control flow: initialization mmaps anonymous shared memory, stores a magic value, initializes rwlock attributes, optionally sets `PTHREAD_PROCESS_SHARED`, initializes the pthread rwlock, destroys attributes, and returns the mapped object. Lock/unlock functions assert the magic value before calling pthread rwlock operations. Remove destroys the rwlock and unmaps the object.

State and persistence: lock state lives in an mmaped `struct fio_rwlock`; the magic constant guards accidental misuse.

Dependencies and integration: pthreads, `sys/mman.h`, fio OS mapping macro `OS_MAP_ANON`, and logging. Used where fio needs shared read/write synchronization across processes or threads.

Risks: `fio_rwlock_init()` error path calls `fio_rwlock_remove()` even if `pthread_rwlock_init()` was not reached, which can destroy an uninitialized rwlock. The assert checks disappear under `NDEBUG`. Process-shared behavior depends on platform support.

Test signals: read/write lock behavior, process-shared operation under `CONFIG_PSHARED`, mmap failure handling, attr/init failure injection, and removal after initialization.
