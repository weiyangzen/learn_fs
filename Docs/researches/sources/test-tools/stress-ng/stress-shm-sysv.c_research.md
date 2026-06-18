# sources/test-tools/stress-ng/stress-shm-sysv.c

Purpose: implements the System V shared memory stressor, creating, attaching, touching, advising, locking, querying, detaching, and removing multiple `shmget` segments per worker while also probing invalid SysV shm API combinations.

Important APIs/types/functions: `stress_shm_sysv`, `stress_shm_sysv_child`, `stress_shm_sysv_get_key`, `stress_shm_sysv_check`, `exercise_shmat`, `exercise_shmctl`, `exercise_shmget`, `stress_shm_metrics`, Linux `stress_shm_get_procinfo` and `stress_shm_sysv_linux_proc_map`, `shmget`, `shmat`, `shmdt`, `shmctl`, `IPC_RMID`, `IPC_STAT`, `SHM_LOCK`, `SHM_UNLOCK`, optional hugepage flags, and NUMA policy shims.

Control flow: the top-level worker computes per-instance byte and segment counts, aligns size to pages, synchronizes start, then repeatedly forks a child and listens on a pipe for allocated shm ids. The child chooses unused keys from a per-instance key range, exercises invalid `shmget` and `shmctl` cases, creates segments with random allowable flags, reports ids to the parent, attaches them, optionally locks memory, touches pages, msyncs/advises, verifies page-pattern contents, queries/sets metadata, optionally probes NUMA and Linux `/proc` map-files, forks a helper to detach/query, then detaches and removes all segments while reporting freed ids. The parent kills/reaps the child, handles OOM/SIGBUS restarts, and removes any segments still reported live.

State and persistence behavior: live SysV segments are kernel-persistent until `IPC_RMID`, so the pipe ledger is critical for cleanup after child death. Child-local arrays track addresses, keys, and ids. Metrics aggregate average nanoseconds per `shmget`, `shmat`, and `shmdt`.

Dependencies and integration points: registered as `CLASS_VM | CLASS_OS | CLASS_IPC`, always verify, with `shm-sysv-bytes`, `shm-sysv-mlock`, and `shm-sysv-segs` options. It uses stress-ng memory-limit/OOM helpers, scheduling helpers, Linux proc hooks, architecture guards, capability-sensitive locking, and System V IPC feature guards.

Risks and test signals: high maximize settings can trigger OOM and leave segments if parent reaping fails. Important signals are leaked shm ids, unexpected `shmget`/`shmat`/`shmdt` failures, memory check failures, bad handling of exhausted keys or ENOSPC, and incorrect skip/error classification for platform-specific commands.
