# sources/test-tools/fio/os/windows/posix/include/semaphore.h

Purpose: placeholder POSIX semaphore header for Windows.

Important APIs/types: none.

Control flow and state: no logic; it exists to satisfy includes.

Dependencies and integration: fio likely uses its own semaphore abstraction (`fio_sem`) on Windows rather than POSIX `sem_t` APIs from this header.

Risks: any code that expects `sem_t`, `sem_init()`, or related APIs from this header will not compile.

Test signals: Windows build coverage after any new semaphore usage.
