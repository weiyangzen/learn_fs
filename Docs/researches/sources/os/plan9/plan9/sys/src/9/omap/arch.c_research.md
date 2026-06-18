# File Research: sources/os/plan9/plan9/sys/src/9/omap/arch.c

Provides OMAP ARM architecture glue for process state, user exit accounting, atomic operations, and kernel process startup.

Key points:
- `setkernur()` fills enough `Ureg` state to show a sleeping proc’s kernel PC/SP and scheduler link register.
- `validalign()` enforces power-of-two address alignment, relaxing 64-bit alignment to 32-bit on this 32-bit ARM environment.
- `kexit()` updates the user-visible `Tos` with kernel cycles, process cycles, cycle frequency, and PID, then writes back/invalidates cache for immediate user visibility.
- `userpc()` returns the last saved user PC from `up->dbgreg`.
- `setregisters()` is a stub that disallows devproc register modification by doing nothing.
- `kprocchild()` initializes kernel process PC/SP and argument state via `linkproc()`.
- `procsetup()`, `procsave()`, and `procrestore()` delegate floating-point state handling and account process cycles.
- `userureg()` identifies user-mode trap frames by PSR mode.
- Provides interrupt-disabled implementations of `_xdec`, `_xinc`, `ainc`, `adec`, and `cas32()`.

Dependencies and interactions:
- Calls FP helpers from `fpiarm.c`/other FP support.
- Uses ARM PSR mode constants from `arm.h`.
- Used by portable proc, devproc, syscall, and scheduler code.

Research relevance:
- Machine-dependent ARM process/accounting glue for the OMAP Plan 9 kernel.
