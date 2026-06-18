# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_prof.c

Implements kernel profiling support for `GPROF`/`DDBPROF` and userland `profil(2)` sampling support, including process profiling output to `gmon.<comm>.<pid>.out`.

When kernel profiling is enabled, `prof_init()` allocates one `struct gmonparam` region per CPU using boot/kernel memory, lays out `tos`, `kcount`, and `froms` tables, computes text boundaries from `KERNBASE` to `etext`, and binds/staggers `ci_gmonclock` clock interrupts. `gmoninit` gates instrumented `mcount()` use until sysctl declares profiling safe.

`prof_state_toggle()` transitions per-CPU profiling on or off. Enabling may patch profiling call sites through DDB profiling support when not built as a profiling kernel, increments `gmon_cpu_count`, starts the profiling clock on first CPU, and advances the CPU clock request. Disabling cancels the CPU clock request, stops the global profiling clock on last CPU, and disables DDB profiling patches.

`sysctl_doprof()` exposes kernel profiling state and buffers per CPU: state, count histogram, froms table, tos arcs, and `gmonparam`. `gmonclock()` updates kernel text histogram buckets when the interrupted frame is kernel mode and profiling is on.

`sys_profil()` implements process profiling. It requires binaries marked with `PSI_PROFILE`, validates scale, stops profiling on scale zero, prevents changing an already established buffer, captures output directory and credentials on first use, records offset/scale/base/sample-size/buffer fields under `splstatclock()`, starts the process profiling clock, and requests rescheduling.

`prof_fork()` holds profiling directory/credential references across fork. `prof_exec()` releases profiling resources and clears the buffer on exec. `prof_write()` writes `gmon` output for a profiling process: it validates user header `totarc`, builds a `gmon.<comm>.<pid>.out` filename from `namei_pool`, temporarily restores the original profiling cwd and credentials, safely opens a regular owner-only file with restrictive checks, truncates it, and writes the user profiling buffer through `vn_rdwr()`.

`profclock()` samples either user PC or process kernel PC when `PS_PROFIL` is set. `addupc_intr()` records pending profile tick state from interrupt context and requests a profiling AST. `addupc_task()` performs faultable user memory update of the profiling counter and disables profiling if copyin/copyout fails.

Filesystem relevance: `prof_write()` is the key filesystem-facing path. It changes process cwd/credential context, uses namei/vnode open/attribute/setattr/close/read-write primitives, and enforces safety constraints before writing profiling output.
