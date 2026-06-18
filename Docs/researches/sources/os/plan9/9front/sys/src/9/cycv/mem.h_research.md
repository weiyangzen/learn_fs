# File Research: sources/os/plan9/9front/sys/src/9/cycv/mem.h

Cyclone V memory layout, page-table flags, processor modes, and assembly constants.

Key contents:
- Defines page/cache-line sizes, stack sizes, timing constants, and max CPUs.
- Defines kernel/user virtual layout: `KZERO`, `KTZERO`, temporary maps, `KMAP`, `MACH`, `MACHL1`, `CONFADDR`, `PERIPH`, `UZERO`, `UTZERO`, and `USTKTOP`.
- Defines Plan 9 PTE abstraction flags and ARM L1/L2 descriptor flags.
- Defines ARM PSR mode/interrupt bits and assembly encodings for barriers, WFE/SEV, CPS, and VFP register access.
- Defines page-table index macros and TTBR attributes.

Role:
- Core memory/MMU ABI for Cyclone V C and assembly code.

Notable constraints:
- Peripheral space begins at `0xFF000000`.
- Temporary mapping sizes are section-sized and tied to L1/L2 layout.
