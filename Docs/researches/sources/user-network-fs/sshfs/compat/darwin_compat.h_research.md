# sources/user-network-fs/sshfs/compat/darwin_compat.h

Purpose: header that maps POSIX semaphore names to Darwin compatibility functions.

Important APIs/types/functions: `darwin_sem_t`, `DARWIN_SEM_VALUE_MAX`, prototypes for all `darwin_sem_*` functions, typedef `sem_t`, and macros mapping `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_post`, `sem_timedwait`, `sem_trywait`, and `sem_wait`.

Control flow: declarations/macros only.

State and persistence behavior: semaphore instances hold count, mutex, and condition variable state.

Dependencies and integration points: included instead of `<semaphore.h>` on Apple builds by `sshfs.c`.

Risks: macro replacement requires callers not to include the system semaphore header. `DARWIN_SEM_VALUE_MAX` is low compared with some systems but enough for request semaphores.

Test signals: Apple compile, macro compatibility with `sshfs.c`, and behavior tests in `darwin_compat.c`.
