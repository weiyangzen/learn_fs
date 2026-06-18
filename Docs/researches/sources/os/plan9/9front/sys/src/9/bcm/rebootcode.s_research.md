# File Research: sources/os/plan9/9front/sys/src/9/bcm/rebootcode.s

32-bit ARM reboot trampoline copied to low physical memory.

Key responsibilities:
- Runs with MMU/caches being torn down for reboot or kernel replacement.
- Copies new kernel/code payload to its destination.
- Cleans/invalidates caches and disables MMU-related state.
- Parks non-boot CPUs with wait-for-interrupt/event loops.
- Branches to the new entry on the boot CPU.

Important behavior:
- Uses physical addresses and explicit cache line maintenance.
- Contains shutdown paths for multicore synchronization.

Dependencies:
- Called by `rebootjump()` after copying to `REBOOTADDR`.
