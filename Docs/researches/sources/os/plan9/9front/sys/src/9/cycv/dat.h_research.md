# File Research: sources/os/plan9/9front/sys/src/9/cycv/dat.h

Cyclone V ARM platform kernel data declarations.

Key contents:
- Defines core architecture typedefs for `Conf`, `Confmem`, `FPsave`, `PFPU`, `L1`, `MMMU`, `PMMU`, `Mach`, `Proc`, `Ureg`, `ISAConf`, and `DMAC`.
- Defines process label, FP state, memory configuration, process MMU state, L1 table wrapper, `Mach`, and ISA config structures.
- Defines DMA attribute bits `SRC_INC` and `DST_INC`.
- Provides memory-mapped register macros for MPCore, reset manager, system manager, L3, and DMA.

Role:
- Shared data ABI for Cyclone V C and assembly files.

Dependencies:
- `mem.h`, `io.h`, Plan 9 port kernel types, and platform MMU/trap code.
