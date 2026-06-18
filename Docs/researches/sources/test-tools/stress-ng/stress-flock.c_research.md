# sources/test-tools/stress-ng/stress-flock.c

Purpose: implements `flock`, a multi-process stressor for BSD file-lock operations on a single shared temporary file.

Important APIs/types/functions: `stress_flock_child()` opens the shared file twice and loops through exclusive locks, nonblocking exclusive locks, shared locks, nonblocking shared locks, invalid lock combinations, invalid fd calls, and `/proc/locks` cache discard on Linux. It measures lock and unlock latency when called by the parent. `stress_flock()` creates the file, forks three synchronized child stressors, runs the same child routine in the parent with metrics enabled, then reaps children.

Control flow: the parent allocates a synchronized pid table, creates a temp file, forks `MAX_FLOCK_STRESSORS` children, sync-starts all workers, and enters the lock loop. The child routine checks that taking an exclusive lock on one fd prevents `LOCK_EX | LOCK_NB` on the second fd, unlocks, exercises invalid fd and invalid operation paths, and increments bogo operations for successful lock cycles until stopped.

State and persistence behavior: creates one temporary file and removes it plus the temp directory on deinit. Runtime state consists of two open read-only fds per process and local timing counters.

Dependencies and integration points: requires `flock()`, `LOCK_EX`, and `LOCK_UN`; shared/nonblocking paths are conditional. Uses stress-ng temp-file, sync pid, kill/wait, bad-fd, metric, and Linux `stress_fs_discard()` helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: lock semantics differ across filesystems and network mounts. The invalid `LOCK_EX | LOCK_SH` combination may be accepted on some kernels or treated differently, so failure expectations should be platform-aware. Opening files read-only while testing locks is fine for flock but may interact with unusual filesystem policies.

Test signals: run on local ext4/xfs/tmpfs and network filesystems if available. Confirm no unexpected double-lock success, metrics for nanoseconds per lock/unlock are emitted, children are SIGALRM reaped, and temp files do not remain.
