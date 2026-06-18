# File Research: sources/os/plan9/9front/sys/src/9/pc/dat.h

Core PC architecture data declarations for the 9front kernel.

Key contents:
- Forward declarations for PC-specific kernel structures such as `Mach`, `PCArch`, `ISAConf`, `Segdesc`, `Ureg`, `PCMslot`, and `BIOS32ci`.
- Floating-point save formats for x87 and SSE plus per-process FPU state.
- Physical memory configuration structs and global `Conf`.
- Per-process MMU state including page directory pages, GDT/LDT descriptors, debug registers, kmap tracking, and VMX pointer.
- x86 task-state segment layout.
- `Mach` CPU-local structure with CPU identity, timing, CPUID feature fields, MMU pools, TSS/GDT pointers, debug state, and stack.
- `PCArch` architecture vtable for reset, interrupts, and clocks.
- CPUID feature bit constants, MSR constants, `ISAConf`, device configuration helpers, and BIOS32 call interface registers.

Role:
- Bridges generic `portdat.h` definitions with PC-specific CPU, MMU, interrupt, firmware, ISA, and architecture-selection state.

Dependencies:
- Included by most PC kernel C files and depends on `mem.h` constants plus `../port/portdat.h`.

Notable constraints:
- Many globals are declared or defined directly in the header, matching Plan 9 kernel build conventions.
- Structure layouts are ABI-sensitive for assembly, trap, MMU, and BIOS call code.
