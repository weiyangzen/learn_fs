# File Research: sources/os/plan9/plan9/sys/src/9/bcm/rebootcode.s

ARMv6 reboot trampoline copied to `REBOOTADDR` and executed during kernel reboot.

Key behavior:
- Entry receives physical entry address, source code address, and byte count.
- Switches to SVC mode with interrupts disabled.
- Calls `cachesoff()` to write back/invalidate caches, disable caches/prediction, double-map physical DRAM and `KZERO`, invalidate TLBs, and relocate `SB`/return address to physical addressing.
- Disables the MMU.
- Sets a tiny physical stack below the new kernel destination.
- Copies the new kernel to its final physical entry address using `memmove()`.
- Branches to the new kernel entry point.

Designed to run safely while dismantling the current virtual-memory environment.
