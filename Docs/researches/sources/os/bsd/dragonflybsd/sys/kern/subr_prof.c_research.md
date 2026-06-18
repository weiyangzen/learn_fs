# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_prof.c

## Summary
Implements process profiling setup and deferred user profiling counter updates.

## Main Responsibilities
- `sys_profil()` handles the profiling syscall, validates scale, installs profiling buffer parameters, and starts/stops the profiling clock.
- `addupc_intr()` records a pending profiling tick from interrupt context.
- `addupc_task()` performs faultable copyin/copyout to update the user sample buffer.

## Important Behavior
Scale is 16-bit fixed point with `0x10000` representing 1.0. Interrupt-side collection only stores the last pending pc/tick pair and requests an AST-style profiling tick. Task-side update disables profiling if user memory copy fails.

## Risks
Ticks can be lost if interrupt updates overwrite pending profile state before the task path runs. The profile buffer is user memory, so bad mappings stop profiling.
