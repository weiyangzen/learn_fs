# File Research: sources/os/bsd/netbsd-src/sys/sys/sem.h

Read completely: 244 lines.

This header defines the System V semaphore ABI and kernel internals. Public types include `struct semid_ds`, `struct sembuf`, semaphore control commands, and userland prototypes for `semctl`, `semget`, `semop`, `semtimedop`, and NetBSD `semconfig`.

Kernel sections define internal `struct __sem`, semaphore limits, permissions, undo structures, configuration defaults, global `seminfo`/`sema`, freeze/thaw commands, sysctl export packing, and implementation functions including `do_semop1`, `do_semop`, `seminit`, `semfini`, `semexit`, and `semctl1`.

Risks: semaphore undo state is per-process and variable-length. ABI structs expose private implementation pointers while sysctl variants handle padding explicitly for 64-bit layouts.
