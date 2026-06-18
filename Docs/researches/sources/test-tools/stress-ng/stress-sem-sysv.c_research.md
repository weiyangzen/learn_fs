# sources/test-tools/stress-ng/stress-sem-sysv.c

Purpose: implements the `sem-sysv` stressor for System V semaphore creation, operation, metadata queries, invalid argument coverage, and multi-process contention. It stresses `semget`, `semop`, optional `semtimedop`, and many `semctl` commands against a shared semaphore set.

Important APIs/types/functions: `stress_semaphore_sysv_init`, `stress_semaphore_sysv_deinit`, `stress_semaphore_sysv_thrash`, `semaphore_sysv_spawn`, `stress_sem_sysv`, `stress_semun_t`, `semget`, `semctl`, `semop`, optional `semtimedop`, Linux `/proc/sysvipc/sem`, `stress_sync_s_pids_mmap`, `stress_sync_start_*`, and `stress_kill_and_wait_many`.

Control flow: initialization probes invalid `semget` cases, chooses an odd key to avoid core-resource collisions, creates a three-semaphore set, and initializes semaphore 0 to 1. `stress_sem_sysv` installs child handling, checks initialization, maps a PID table, spawns the configured number of children, releases them after the parent sync point, then waits until the run ends and kills/reaps them. Each child loops through timed or normal wait/signal operations, increments bogo ops, periodically reads proc info, exercises `IPC_STAT`/`IPC_SET`, `GETALL`, optional `SETALL`, Linux info/stat commands, value/count queries, invalid `semctl` commands, invalid `semop`/`semtimedop` arguments, and a direct `__NR_semctl` syscall when available.

State and persistence behavior: the shared semaphore id/key/init flag live in `g_shared->sem_sysv` across workers and are removed in deinit via `IPC_RMID`. Child state is process-local except for semaphore mutations and `SEM_UNDO` adjustments. `sem-sysv-setall` can intentionally perturb semaphore values, so it is option-controlled.

Dependencies and integration points: registered with `.init` and `.deinit`, `CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, always verify, and options `sem-sysv-procs` and `sem-sysv-setall`. It depends on System V IPC headers, stress-ng synchronization helpers, kill/reap helpers, and Linux-only proc/stat commands behind guards.

Risks and test signals: resource limits can cause skip/no-resource exits if the set cannot be created or PIDs cannot be mapped. Important signals are unexpected semaphore operation failures, semaphore leaks after deinit, hangs in child waits, incorrect handling of `semtimedop` availability, or invalid-argument probes accidentally mutating the live set beyond recovery.
