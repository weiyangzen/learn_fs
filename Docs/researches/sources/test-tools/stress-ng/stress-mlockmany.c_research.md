# sources/test-tools/stress-ng/stress-mlockmany.c

Purpose: `stress-mlockmany.c` stresses page locking by repeatedly forking many child processes that each mmap, touch, mlock/munlock, and then are killed/reaped. It is classified pathological because it can create many processes and pressure locked-memory and swap accounting.

Important APIs/types/functions: `stress_mlock_interruptible` and `stress_munlock_interruptible` lock/unlock in 16-page chunks while respecting `stress_continue(args)` and memory-low checks. `stress_mlockmany_child` is the OOM-contained main workload; `stress_mlockmany` wraps it with `stress_oomable_child`. The option `--mlockmany-procs` controls process fan-out with defaults based on stressor instances.

Control flow: the child drops capabilities to make OOM behavior more likely, derives process count, mmaps a shared PID array, gets `RLIMIT_MEMLOCK` or fallback lock size, synchronizes, then loops. For each cycle it initializes PID slots, tracks memory and swap limits, forks children until requested count, swap use, time, or failure stops it. Each forked child installs parent-death behavior, tries invalid `mlockall(0)`, calls `munlockall`, scales down mmap/lock sizes until successful, touches/advises pages, alternates munlock/mlock, tries zero and oversized lock/unlock calls, sleeps briefly, then exits when asked. Parent kills and waits for all children each cycle.

State and persistence behavior: state is transient process state, anonymous mappings, kernel locked-memory accounting, and shared PID mappings. No files are created. Swap free counters are used as a safety signal to stop forking if swap begins to be consumed.

Dependencies and integration points: the file depends on fork/wait, killpid helpers, capability dropping, madvise/mincore helpers, memory limit helpers, OOM adjustment, and `mlock` shims. It registers `stress_mlockmany_info` as `CLASS_VM | CLASS_OS | CLASS_PATHOLOGICAL`; missing `mlock` builds register unimplemented.

Risks: large `--mlockmany-procs` values can overwhelm process tables, scheduler, and memory lock limits; defaults scale by instance count but still may be high. Parent cleanup must kill and reap children reliably. Swap detection is heuristic and depends on `stress_memory_limits_get`. Dropping capabilities changes child behavior and should remain child-scoped.

Test signals: run `stress-ng --mlockmany 1 --mlockmany-ops 1 --mlockmany-procs 2`, then a default run on a safe test host. Check that children are reaped, no live child processes remain, and the unimplemented path compiles when `HAVE_MLOCK` is absent.
