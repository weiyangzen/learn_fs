# File Research: sources/os/bsd/freebsd-src/sys/sys/sem.h

System V semaphore ABI and kernel-private wrapper declarations.

Key responsibilities:
- Defines public SysV semaphore structures: `semid_ds`, `sembuf`, and optionally `semun`.
- Preserves older ABI layouts through `semid_ds_old` and `semun_old` under compatibility options.
- Defines `semctl()` command constants such as `GETVAL`, `SETVAL`, `GETALL`, `SEM_STAT`, and `SEM_INFO`.
- Defines semaphore permission aliases `SEM_A` and `SEM_R`.
- Under kernel/internal visibility, defines `seminfo`, `semid_kernel`, and allocation/destroy mode bits.

Important patterns:
- User ABI is kept separate from kernel metadata by wrapping `semid_ds` in `semid_kernel` with MAC label and creator credentials.
- `_WANT_SYSVSEM_INTERNALS` triggers inclusion of broader SysV IPC internals.
- Kernel exposes `semexit()` for undo cleanup at process exit and `kern_get_sema()` for introspection/export.

Research relevance:
- Defines FreeBSD's SysV semaphore contract and the compatibility surface needed by older binaries.
