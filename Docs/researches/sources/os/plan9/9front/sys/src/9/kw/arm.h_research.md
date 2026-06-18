# File Research: sources/os/plan9/9front/sys/src/9/kw/arm.h

Defines ARM processor constants for the Kirkwood kernel port.

Key elements:
- Defines PSR mode and condition bits.
- Defines coprocessor numbers and CP15 register/opcode constants.
- Defines cache, TLB, barrier, and L2 test/config operation constants.
- Defines ARM page-table entry bits for sections and small/large pages.
- Defines domain/access permission helpers and high-vector address.

Dependencies:
- Included by platform C and assembly code that manipulates ARM system registers and MMU state.

Research notes:
- Comments distinguish ARM architectural terminology where “flush” means invalidate and “clean” means writeback.
- Several constants target ARM926EJ-S/Sheeva-specific L2 behavior.
