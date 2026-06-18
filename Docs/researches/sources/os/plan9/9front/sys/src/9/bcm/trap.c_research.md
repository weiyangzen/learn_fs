# File Research: sources/os/plan9/9front/sys/src/9/bcm/trap.c

32-bit ARM trap, syscall exception, fault, and diagnostic handling for BCM.

Key responsibilities:
- Installs exception vectors in `trapinit()`.
- Converts ARM trap modes/status into printable names.
- Handles ARM data/prefetch faults through `faultarm()`.
- Detects write faults from instruction decoding with `writetomem()`.
- Dispatches IRQ/FIQ, syscall, undefined instruction, and abort cases in `trap()`.
- Produces user notes or exits for user-mode faults.
- Provides stack/register dumps and `callwithureg()` diagnostics.

Important behavior:
- Distinguishes user and kernel traps via PSR mode.
- Kernel faults panic unless handled by `waserror()`/fault recovery paths.
- Maintains interrupt nesting and scheduling behavior around clock IRQs.

Dependencies:
- Exception assembly, Plan 9 fault VM code, note delivery, scheduler, interrupt controller, and ARM fault-status registers.
