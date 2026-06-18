# File Research: sources/os/plan9/9front/sys/src/9/zynq/l.s

Purpose: Main Zynq ARM assembly support file: early boot, MMU/cache setup, CPU bootstrap, user transitions, synchronization primitives, TLB/cache maintenance, performance counters, and VFP save/restore.

Key behavior:
- `_start` clears config space, builds initial section/page mappings, maps UART for debug output, enables MMU, and jumps to virtual address space.
- `_virt` sets stacks, vector base, VFP permissions, L1 cache, TPIDRPRW Mach pointer, and calls `main`.
- `mpbootstrap` starts CPU1 using its own Mach/L1 setup.
- `touser` and `forkret` restore user state.
- Implements `spllo`, `splhi`, `splx`, `islo`, labels, CAS/TAS, barriers, idle/event instructions.
- Implements TTB/TLB/FAR/FSR accessors, performance counter access, cycle counter high-word maintenance, VFP init/save/restore/off.
- Implements cache clean/invalidate operations by range and line.

Integration notes: Exports many functions declared in `fns.h`; depends on offsets/layout in `mem.h` and `dat.h`.

Risk/attention points: Assembly depends on exact `Mach` offsets and ARM control-register semantics. Early UART debug writes assume a specific UART MMIO address.
