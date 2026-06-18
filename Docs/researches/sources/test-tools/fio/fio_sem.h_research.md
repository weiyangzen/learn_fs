# sources/test-tools/fio/fio_sem.h

Purpose: declares fio's process-capable counting semaphore structure and API.

Important APIs/types/functions: defines `FIO_SEM_MAGIC`, `struct fio_sem` with `pthread_mutex_t lock`, `pthread_cond_t cond`, `int value`, `int waiters`, and `uint32_t magic`; lock-state constants `FIO_SEM_LOCKED` and `FIO_SEM_UNLOCKED`; and prototypes for normal mmap semaphores, shared-memory semaphores, blocking/timeout/trylock down operations, and up/removal operations.

Control flow: consumers use `fio_sem_init` or `fio_shared_sem_init`, then pair `fio_sem_down`/`fio_sem_up` or use timeout/trylock variants. `__fio_sem_init` and `__fio_sem_remove` are exposed for callers embedding a semaphore in another allocation.

State and persistence behavior: the header fixes the in-memory layout used by both mmap-backed and fio shared-memory-backed semaphores. There is no file persistence; state must be valid across pthreads and, when process-shared attributes are available, forked workers.

Dependencies/integration: includes pthreads and fio integer types. It is consumed by synchronization-heavy fio modules including file locking, flow control, gettime offload startup, and other job coordination code.

Risks and test signals: any layout or magic-value change affects users that allocate semaphores in shared memory. Tests should include compilation on platforms with and without process-shared condattr support, embedded semaphore lifecycle, and misuse detection via magic assertions.
