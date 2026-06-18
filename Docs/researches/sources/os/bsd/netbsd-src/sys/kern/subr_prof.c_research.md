# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_prof.c

## Purpose
Provides kernel and user profiling support. When `GPROF` is enabled it allocates and exposes kernel gprof buffers through `kern.profiling`; regardless of `GPROF`, it implements the `profil(2)` syscall and profile tick accounting for user processes.

## Main Entry Points
- Under `GPROF`: `kmstartup()` allocates kernel profiling buffers; `sysctl_kern_profiling()` serves and updates profiling sysctls; `sysctl_kern_gprof_setup` creates the sysctl tree; `prof_set_state_xc()` updates per-CPU state on MP builds.
- User profiling: `sys_profil()` configures a process profiling buffer and starts/stops the profiling clock.
- Tick handling: `addupc_intr()` records pending profile ticks from interrupt context and schedules an AST; `addupc_task()` performs faultable user-buffer updates later.

## Control Flow And State
`kmstartup()` computes text bounds, histogram/from/to buffer sizes, and either allocates a single buffer set or per-CPU `struct gmonparam` blocks on multiprocessor kernels. MP builds expose per-CPU sysctl subtrees and can merge per-CPU data for global reads. Sysctl writes to state start/stop `proc0`'s profiling clock and broadcast/unicast state changes to CPUs; writes to global profiling arrays propagate data to per-CPU arrays.

`sys_profil()` validates fixed-point scale, disables profiling for scale zero, or installs base/size/offset/scale under the process statistics mutex. `addupc_intr()` checks range under the same mutex, drops it to update pending tick fields, and requests a profiling AST. `addupc_task()` later copies the 16-bit sample counter from user memory, adds ticks, writes it back, and disables profiling on copy failure.

## Dependencies
Uses gprof structures, malloc type `M_GPROF`, sysctl, CPU iteration and xcalls, process statistics locks, profile clocks, copyin/copyout, AST/profile tick hooks, and optional multiprocessor support.

## Risks And Notes
MP kernel profiling has compatibility behavior where global `_gmonparam.state` can override per-CPU state. Merged reads allocate temporary profiling storage and can fail with `ENOMEM`. User profiling intentionally may lose ticks if AST delivery lags. Failed user buffer access in `addupc_task()` stops profiling rather than retrying.
