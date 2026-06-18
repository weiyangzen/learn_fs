# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arch.c

ARM/Tegra process and trap-glue routines that connect the generic Plan 9 kernel to Cortex-A9 register, timing, and process-state conventions.

Key responsibilities:
- Builds minimal kernel `Ureg` context for sleeping processes in `setkernur`.
- Implements architecture alignment checks for syscall/file/proc paths, relaxing 64-bit alignment to 32-bit alignment.
- Updates the user `Tos` structure on kernel exit with kernel cycles, process cycles, cycle frequency, and PID, then writes it back from cache.
- Provides user PC, debug PC, kernel process child setup, process setup/save/restore, and user-ureg detection.
- Delegates floating-point process lifecycle to FPU helpers.

Dependencies and assumptions:
- Depends on ARM `Ureg` layout, `sched`, `cycles`, `l1cache`, and VFP support routines.
- Assumes ARM user mode is identified by `(psr & PsrMask) == PsrMusr`.

Notable risks:
- `setregisters` is a stub, so devproc register writes are effectively ignored for this port.
- `procrestore` performs a full L1 writeback because the comment says the system is more stable with it.
