# File Research: sources/os/plan9/plan9/sys/src/9/bcm/lexception.s

ARM exception vector and trap-entry assembly.

Key behavior:
- Defines `vectors` and `vtable`, copied to high vectors by `trapinit()`.
- `_vsvc` handles SWI/syscall directly in SVC mode, builds a `Ureg`, loads kernel `SB`, `m`, and `up`, calls `syscall()`, restores registers/SPSR, and returns with `RFE`.
- `_vund`, `_vpabt`, `_vdabt`, and `_virq` save scratch registers in the exception mode, switch to SVC mode, build `Ureg`, and call `trap()`.
- Separates user and kernel exception paths because user register restore uses `.S` banked-register behavior.
- `_vfiq` builds a `Ureg` and calls `fiq()`.
- `setr13()` sets the banked stack pointer for a requested CPU mode and returns the old SP.

This file is tightly coupled to `trap.c`, `dat.h` Mach save areas, and `ureg.h`.
