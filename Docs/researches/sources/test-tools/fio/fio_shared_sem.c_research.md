# sources/test-tools/fio/fio_shared_sem.c

Purpose: provides shared-memory allocation wrappers for `fio_sem`, separated from `fio_sem.c` to avoid a circular dependency between semaphore code and fio's shared allocator.

Important APIs/types/functions: exports `fio_shared_sem_init(int value)` and `fio_shared_sem_remove(struct fio_sem *sem)`.

Control flow: initialization allocates semaphore storage with `smalloc`, calls `__fio_sem_init`, and returns the semaphore on success. On initialization failure it calls `fio_shared_sem_remove`, which destroys pthread state with `__fio_sem_remove` and returns storage with `sfree`.

State and persistence behavior: semaphore state is held in fio shared memory rather than anonymous mmap. This allows a parent process to free semaphores allocated by child processes as part of fio's shared memory lifetime. There is no durable persistence beyond process/shared-memory lifetime.

Dependencies/integration: depends on `fio_sem.h` for the common semaphore implementation and `smalloc.h` for fio shared allocations. It is the right constructor for locks stored in structures shared across fio worker processes.

Risks and test signals: correct behavior depends on `smalloc` lifetime and process-shared pthread initialization. Test signals should cover child-created locks, parent cleanup, failed allocation, failed `__fio_sem_init`, and mixed use with ordinary `fio_sem_remove` avoided.
