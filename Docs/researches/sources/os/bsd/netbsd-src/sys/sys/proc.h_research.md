# File Research: sources/os/bsd/netbsd-src/sys/sys/proc.h

## Purpose
Defines NetBSD process/session/process-group structures, emulation hooks, process state flags, fork/wait/sleep/process-management kernel APIs, and kernel stack parameter defaults.

## Main API
- Structures: `struct session`, `struct pgrp`, `struct sc_autoload`, `struct emul`, `struct proc`, `struct proclist_desc`.
- Process status values: `SIDL`, `SACTIVE`, `SDYING`, `SSTOP`, `SZOMB`, `SDEAD`; helper `P_ZOMBIE`.
- Process flags: `PK_*`, `PS_*`, `PSL_*`, `PST_PROFIL`, `PL_*`.
- Helpers: `P_EXITSIG`, `P_WAITSTATUS`, `SESS_LEADER`, `PROC_PTRSZ`, `PROC_REGSZ`, `PROC_FPREGSZ`, `PROC_DBREGSZ`, `PROC_MACHINE_ARCH`, `PROCLIST_FOREACH`.
- Fork flags: `FORK_PPWAIT`, `FORK_SHAREVM`, `FORK_SHARECWD`, `FORK_SHAREFILES`, `FORK_SHARESIGS`, `FORK_NOWAIT`, `FORK_CLEANFILES`, `FORK_SYSTEM`.
- Kernel globals: `proc0`, `nprocs`, `maxproc`, `proc_lock`, `allproc`, `zombproc`, `initproc`, `emul_netbsd`.
- Process APIs: find/lookup, process group/session management, `tsleep`, `mtsleep`, `wakeup`, `kpause`, `exit1`, `kill1`, wait helpers, proc allocation/free, fork, credential/VM helpers, proc-specific data, kqueue notifications.
- Stack macros: `KSTACK_LOWEST_ADDR`, `KSTACK_SIZE`.

## Dependencies
Includes `sys/lwp.h`; kernel/kmem-user sections pull machine proc/pcb, aio, idtype, locks, mqueue, queues, radixtree, signal/event/specificdata, resources, and UVM-related types through referenced structures.

## Risks and Notes
The `struct proc` field comments encode lock ownership and stability requirements. Creation zero/copy ranges are defined by marker macros, making layout changes sensitive. Many APIs require holding `proc_lock` or `p_lock`; incorrect locking can break process lifetime, tracing, wait, and signal behavior.
