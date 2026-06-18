# sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.h

Purpose: Declares the Darwin semaphore compatibility API and maps POSIX semaphore names to the local implementation.

Important APIs/types/functions: Defines `darwin_sem_t` with local count/mutex/condition storage, `DARWIN_SEM_VALUE_MAX`, function prototypes for the Darwin semaphore operations, `typedef darwin_sem_t sem_t`, and macros `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_post`, `sem_timedwait`, `sem_trywait`, and `sem_wait`.

Control flow: This header is included instead of `<semaphore.h>` on Darwin through `pyfuse3.h`, so C/Cython code can call semaphore APIs under the standard names.

State and persistence: Defines the memory layout used by `darwin_compat.c`; no persistent state.

Dependencies and integration points: Requires `pthread.h`. It integrates with the platform selector in `pyfuse3.h` and must not be combined with the system semaphore header in the same caller.

Risks: Macro substitution can surprise code that expects real POSIX semaphore types. `DARWIN_SEM_VALUE_MAX` depends on `int32_t`, so transitive includes must provide it on all supported compilers.

Test signals: Covered only by Darwin compilation/runtime paths.
