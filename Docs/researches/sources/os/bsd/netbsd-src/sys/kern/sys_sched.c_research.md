# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_sched.c

Implements NetBSD scheduler-related syscalls: POSIX scheduling policy/priority, CPU affinity, priority protection, yield, sysctl exposure, and kauth policy defaults.

Key entry points:
- `sys__sched_setparam` / `do_sched_setparam`: validates policy and realtime priority, finds process/LWP targets, rejects system processes, authorizes via `KAUTH_PROCESS_SCHEDULER_SETPARAM`, updates `l_class` and priority with `lwp_changepri`.
- `sys__sched_getparam` / `do_sched_getparam`: resolves a target LWP, authorizes, reads class/priority, converts kernel priority back to user-visible scheduler priority.
- `sys__sched_setaffinity`: copies in a CPU set, validates CPUs against processor sets/offline state under `cpu_lock`, authorizes, applies affinity to one or more LWPs, and migrates them.
- `sys__sched_getaffinity`: returns the target LWP affinity mask or an all-zero mask when no affinity is set.
- `sys__sched_protect`: implements a weak priority-protection mechanism for `PTHREAD_PRIO_PROTECT`, tracking protect depth and auxiliary priority.
- `sys_sched_yield`: invokes `yield()`.
- `sched_init`: installs scheduler sysctls and a kauth listener.

Important helpers and state:
- `convert_pri` translates between POSIX realtime priorities and NetBSD internal priorities, with special handling for `SCHED_OTHER`.
- `genkcpuset` allocates and imports user CPU masks.
- `sched_listener_cb` allows owners to query scheduling parameters and allows non-privileged setparam only for same-owner, non-realtime-escalating cases; affinity setting is left privileged for secmodel policy.

Concurrency/locking:
- The file documents lock order: `cpu_lock -> proc_lock -> p_lock -> lwp_lock`.
- Affinity changes hold `cpu_lock` across CPU-set validation and LWP updates to avoid races with CPU online/offline and processor-set state.
- Process/LWP traversal is protected by `proc_lock`, `p_lock`, and `lwp_lock` as appropriate.

Research notes:
- This is not filesystem code directly, but it is core process/LWP syscall infrastructure that interacts with user/kernel copying, authorization, and CPU scheduling state.
