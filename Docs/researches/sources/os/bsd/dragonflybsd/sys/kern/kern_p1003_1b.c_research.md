# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_p1003_1b.c

This file provides POSIX.1b realtime common code and syscall glue for POSIX priority scheduling. It either returns `ENOSYS` for scheduling syscalls when `_KPOSIX_PRIORITY_SCHEDULING` is not configured, or forwards those syscalls to the `ksched` layer when configured.

Modes:
- Without `_KPOSIX_PRIORITY_SCHEDULING`, generated syscall stubs log attempted use and return `ENOSYS`.
- With `_KPOSIX_PRIORITY_SCHEDULING`, the file implements process lookup/permission checks and forwards scheduling operations to `ksched_*()` functions.

Important functions when configured:
- `p31b_proc()` resolves `pid == 0` to the current process or uses `pfind()`, checks `CAN_AFFECT`, holds the target process, and takes its process token.
- `p31b_proc_done()` releases the token and process reference.
- `sched_attach()` attaches `ksched` and advertises `CTL_P1003_1B_PRIORITY_SCHEDULING`.
- `sys_sched_setparam()`, `sys_sched_getparam()`, `sys_sched_setscheduler()`, `sys_sched_getscheduler()`, and `sys_sched_rr_get_interval()` operate on the first LWP in the target process and call the corresponding `ksched` operation.
- `sys_sched_yield()`, `sys_sched_get_priority_max()`, and `sys_sched_get_priority_min()` are MPSAFE simple wrappers.
- `p31binit()` publishes POSIX.1b facility values through `p31b_setcfg()`.

Permissions and limitations:
- `CAN_AFFECT` is currently restricted to uid 0 in the active code path.
- Process-level scheduling syscalls still contain `/* XXX lwp */` notes and act on `FIRST_LWP_IN_PROC()`, so they do not fully model multi-LWP selection.

Filesystem/storage relevance:
- Not filesystem code, but realtime scheduling can affect latency-sensitive kernel/user workloads, including storage daemons and filesystem maintenance tools.
