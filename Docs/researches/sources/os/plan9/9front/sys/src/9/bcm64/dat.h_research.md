# File Research: sources/os/plan9/9front/sys/src/9/bcm64/dat.h

ARM64 BCM kernel data structure declarations and platform configuration types.

Key contents:
- Defines core typedefs for `Mach`, `Proc`, `PMMU`, `MMMU`, `Conf`, `FPsave`, `FPalloc`, `PFPU`, `Uart`, `Pcidev`, and `Soc`.
- Defines `Label`, FP state, memory-bank config, global configuration, process/MMU state, and `Mach`.
- Defines ISA config parsing structure and debug flags.
- Defines device config and SoC-dependent physical/virtual I/O, RAM, PCI, and page-table attributes.
- Provides timing constants and kernel ABI constants.

Role:
- Shared architecture data contract for ARM64 BCM C and assembly code.

Dependencies:
- `mem.h` address constants, Plan 9 port layer types, and ARM64-specific trap/MMU code.
