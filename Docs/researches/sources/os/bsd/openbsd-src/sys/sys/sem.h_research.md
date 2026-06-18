# File Research: sources/os/bsd/openbsd-src/sys/sys/sem.h

Defines System V semaphore ABI, sysctl metadata, and kernel semaphore implementation structures.

Key contents:
- BSD-visible sysctl IDs for `struct seminfo` members.
- Public `struct sem`, `struct semid_ds`, `struct sembuf`, and `union semun`.
- `SEM_UNDO`, semctl commands, and permission bits.
- Kernel constants `SEMVMX` and `SEMAEM`.
- Kernel `struct semid_ds_kern` with `struct refcnt`.
- `struct sem_undo` with flexible undo entries.
- `struct seminfo`, `struct sem_sysctl_info`, defaults for `SEMMNI`, `SEMMNS`, `SEMUME`, `SEMMNU`, `SEMMSL`, `SEMOPM`, and `SEMUSZ`.
- Global `seminfo` and semaphore ID list `sema`.

Key APIs:
- Kernel: `seminit`, `semexit`, `sysctl_sysvsem`.
- Userland: `semctl`, `__semctl`, `semget`, `semop`.

Risk notes:
- Undo structure sizing depends on `SEMUME`; semaphore IDs are refcounted in-kernel to protect concurrent operations.
