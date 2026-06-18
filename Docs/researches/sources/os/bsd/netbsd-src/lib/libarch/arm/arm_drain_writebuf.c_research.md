# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_drain_writebuf.c

Tiny public wrapper for the ARM write-buffer drain operation.

Key behavior:
- Exports `int arm_drain_writebuf(void)`.
- Calls `sysarch(ARM_DRAIN_WRITEBUF, NULL)` and returns the syscall result unchanged.

Dependencies:
- `machine/sysarch.h` for `ARM_DRAIN_WRITEBUF`.
- Kernel support for the ARM `sysarch` operation.

Notes:
- No local validation or retry behavior; all error reporting comes through `sysarch`.
