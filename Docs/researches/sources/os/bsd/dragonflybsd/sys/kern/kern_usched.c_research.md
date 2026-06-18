# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_usched.c

Implements user scheduler registration/control plus CPU affinity syscalls for processes and LWPs.

Key global state:
- `usched_list`: registered user schedulers.
- `usched_mastermask`: all-ones CPU mask.

Key APIs:
- `usched_init()`
- `usched_ctl()`
- `usched_schedulerclock()`
- `sys_usched_set()`
- `sys_lwp_getaffinity()`
- `sys_lwp_setaffinity()`
- `setaffinity_lp()`

Important behavior:
- `usched_init()` registers `bsd4`, `dfly`, and `dummy` schedulers during early boot and chooses default from `kern.user_scheduler`, defaulting to `dfly`.
- `usched_ctl()` adds/removes schedulers, invoking optional register/unregister callbacks and disallowing removal of `bsd4`.
- `usched_schedulerclock()` calls each registered scheduler’s clock hook, passing the current LWP only to its owning scheduler.
- `sys_usched_set()` handles scheduler selection and older CPU-affinity commands. Scheduler changes require single-threaded processes and `SYSCAP_NOSCHED`; CPU mask mutation generally requires `SYSCAP_NOSCHED_CPUSET`.
- `sys_lwp_getaffinity()` snapshots the active CPU mask for a selected process/LWP.
- `sys_lwp_setaffinity()` updates one LWP or all LWPs in a process and allows self-affinity changes without privilege otherwise required for other processes.
- `setaffinity_lp()` updates `lwp_cpumask` and immediately migrates the current LWP if its current CPU is no longer allowed.

Concurrency model:
- Process and LWP tokens protect tree lookup and affinity mutation.
- Process references use `PHOLD/PRELE`; LWP references use `LWPHOLD/LWPRELE`.

Filesystem relevance:
- No direct filesystem implementation. Scheduler choice and CPU affinity can materially affect VFS/filesystem workload scheduling, per-CPU cache locality, and latency.
