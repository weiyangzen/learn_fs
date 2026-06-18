# File Research: sources/os/plan9/9front/sys/src/9/bcm/arm.s

Shared ARMv6/v7 assembly macro definitions.

Key behavior:
- Defines physical address and L1 index macros.
- Provides assembler macro forms for barriers, `MCRR`, `MRRC`, `MSR`, CPS interrupt enable/disable, debug GPIO pulse, and CPU ID detection.
- Supplies default ARMv6-style barrier implementations overridden by ARMv7 assembly.

Dependencies:
- Included by `armv6.s` and `armv7.s`.

Research notes:
- This file is macro infrastructure, not standalone executable code.
