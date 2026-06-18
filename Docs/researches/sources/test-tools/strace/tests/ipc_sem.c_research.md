<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem.c -->
# sources/test-tools/strace/tests/ipc_sem.c

Purpose: Tests SysV semaphore decoding for `semget` and `semctl`, including semaphore metadata and Linux info/stat commands.

Important APIs/types/functions: Uses `semget`, `semctl`, local `union semun`, `struct semid_ds`, `struct seminfo`, `cleanup`, `print_semid_ds`, `print_sem_info`, and resource flag xlat strings.

Control flow: Prints a bogus `semget`, creates a private semaphore set, registers cleanup, optionally tests a bogus command, prints `IPC_INFO` and `SEM_INFO`, reads `IPC_STAT`, writes `IPC_SET`, and prints `SEM_STAT`. `SEM_STAT_ANY` is intentionally disabled due libc argument-passing bugs noted in comments.

State/persistence behavior: Creates one semaphore set and removes it with `IPC_RMID` through `atexit`. No state should remain after successful exit.

Dependencies: Requires SysV semaphore support, glibc guard behavior for invalid commands, and strace xlat tables for resource flags and IPC command names.

Integration points: Verifies semctl argument decoding across raw/verbose/abbrev xlat modes, optional `IPC_64` rendering, and structure field extraction.

Risks: libc wrappers differ for unsupported commands; semaphore limits can prevent object creation. The disabled `SEM_STAT_ANY` branch documents a known libc interface hazard.

Test signals: Expected output includes bogus and private `semget`, info/stat structures, `IPC_SET`, cleanup line, and no final explicit exit marker in this file.

Source read signal: complete file read for this research pass; file size 241 line(s), 6931 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem.c -->
