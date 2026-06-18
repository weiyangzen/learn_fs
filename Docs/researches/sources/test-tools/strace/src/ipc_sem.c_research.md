# sources/test-tools/strace/src/ipc_sem.c

Purpose: decodes SysV semaphore operation and creation syscalls.

Important APIs/types/functions: `SYS_FUNC(semop)`, `SYS_FUNC(semtimedop_time32)`, `SYS_FUNC(semtimedop_time64)`, `SYS_FUNC(semget)`, `print_sembuf`, `tprint_sembuf_array`, `do_semtimedop`, and xlats `semop_flags`, `ipc_private`, `resource_flags`.

Control flow: semaphore operations print `semid`, then decode a `struct sembuf` array from either direct arguments or legacy indirect IPC slots. Timed operations share `do_semtimedop`, selecting `print_timespec32` or `print_timespec64` and using an S390/S390X-specific timeout slot for indirect calls. `semget` prints key, count, and resource/mode flags.

State and persistence behavior: no persistent state. Tracee memory reads are bounded by `nsops` and handled through `print_array`.

Dependencies and integration points: uses provider headers selected by `ipc_defs.h`, generic time printers, SysV IPC flags, and indirect IPC detection.

Risks: argument positions differ between direct, indirect, and S390 legacy paths. Large `nsops` values can produce abbreviated arrays depending on strace settings and memory availability.

Test signals: cover direct and indirect `semop`, timed 32/64 variants, S390-specific argument mapping where applicable, `SEM_UNDO`/`IPC_NOWAIT`, IPC_PRIVATE, and permission mode rendering.
