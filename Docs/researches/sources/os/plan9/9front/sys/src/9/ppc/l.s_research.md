# File Research: sources/os/plan9/9front/sys/src/9/ppc/l.s

PowerPC assembly runtime, exception entry, MMU bootstrap, cache, FP, and special-register support.

Key responsibilities:
- Defines reset/start path: disables interrupts, sets SB, enters virtual mode through BAT setup, sets `m`/stack, and calls `main()`.
- Builds early BAT mappings for kernel memory, FPGA, and internal memory, with alternate UCU setup.
- Provides FP initialization, FP save/restore, SPL operations, label save/restore, user transition, cache flush/invalidate helpers, atomic test-and-set, TLB flush/load helpers, and direct special-register accessors.
- Implements fast instruction/data TLB miss handlers that search the hashed page table and load PPC 603e TLB entries.
- Implements trap-vector and TLB-vector assembly, saving a full `Ureg`, restoring state, and returning with `RFI`.
- Provides cache enable/disable and optional UCU L2/BAT helper routines.
- Provides MMU-disable/reboot support and `mul64fract()`.

Dependencies:
- Must match `Mach` and `Ureg` offsets in C headers and uses constants from `mem.h`.

Notable behavior:
- Trap entry handles user versus kernel stack selection before enabling the MMU and calling C `trap()`.
- The code uses SPRG registers as temporary save slots during exceptions.
