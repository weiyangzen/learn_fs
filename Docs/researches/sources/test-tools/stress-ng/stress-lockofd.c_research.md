# sources/test-tools/stress-ng/stress-lockofd.c

Purpose: implements `lockofd`, a focused open-file-description locking stressor. It stresses Linux/OFD `fcntl()` lock operations over random byte ranges in a shared file.

Important APIs/types/functions: `stress_lockofd_info_t` stores offset and length for each held OFD lock. The list helpers allocate/reuse records, remove the head, and free active/free lists. `stress_lockofd_unlock()` issues `fcntl(fd, F_OFD_SETLK, F_UNLCK)`. `stress_lockofd_contention()` creates random write locks with `F_OFD_SETLK`. `stress_lockofd()` owns temp file setup, child fork, synchronization, and registration.

Control flow: after creating a 1 MiB temp file, the stressor fills it, synchronizes, forks, and runs parent/child contention loops against the same file description. Each loop keeps at most `LOCK_MAX` held ranges, unlocking the oldest when the list is full. Failed lock attempts are normal and simply continue.

State and persistence: only the per-process lock list persists across iterations. Temporary file and directory are unlinked at shutdown. The child process is killed and waited during cleanup.

Dependencies/integration: gated by `F_OFD_GETLK`, `F_OFD_SETLK`, `F_OFD_SETLKW`, `F_WRLCK`, and `F_UNLCK`. Uses temp-file, affinity, fork retry, scheduler, proc-state, and kill helpers.

Risks/test signals: OFD locks are Linux-specific and tied to open file descriptions rather than process IDs, so descriptor sharing across fork is intentional. Useful signals are build-time unimplemented behavior, bogo progress, temp cleanup, and no retained lock records after exit.
