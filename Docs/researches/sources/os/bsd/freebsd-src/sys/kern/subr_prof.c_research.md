# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prof.c

## Purpose
Implements the `profil(2)` system call and user-mode profiling sample updates.

## Main Interfaces
- `sys_profil()`: enables/disables profiling for the calling process.
- `addupc_intr()`: records a pending profiling tick from interrupt context.
- `addupc_task()`: performs the actual user profiling buffer update in a context where copyin/copyout are allowed.

## Implementation Notes
Profiling uses a fixed-point scale with 16 fractional bits; `scale == 0` disables profiling. `sys_profil()` validates scale, updates `p_stats->p_prof` under process/profile locks, and starts or stops the profiling clock.

`PC_TO_INDEX()` maps a program counter to a sample-buffer byte offset: `(pc - offset) * scale >> 16`, rounded down to an even address for `u_short` counters.

`addupc_intr()` is interrupt-safe: it checks range under `PROC_PROFLOCK`, then stores the PC/tick count in thread fields, sets `TDP_OWEUPC`, and schedules an AST. It may lose samples if overloaded and a later tick overwrites pending state.

`addupc_task()` runs later, validates the process is still profiling, increments `p_profthreads`, computes the target address, unlocks around `copyin`/`copyout`, adds ticks to the 16-bit counter, and stops profiling if user buffer access fails. It coordinates with `P_STOPPROF` waiters.

## Dependencies
Uses process/profile locks, AST scheduling, copyin/copyout, profiling clock hooks, and process statistics.

## Research Notes
This is process accounting/profiling infrastructure. It is not filesystem-specific, but profiling can be used to measure filesystem-heavy workloads.
