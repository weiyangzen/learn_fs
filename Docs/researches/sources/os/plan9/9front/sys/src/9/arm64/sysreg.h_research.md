# File Research: sources/os/plan9/9front/sys/src/9/arm64/sysreg.h

ARM64 system register and barrier operand encoding definitions.

Key definitions:
- Encodes many EL1/EL2/EL0 system registers with `SYSREG`.
- Covers CPU ID, MMU, exception, timer, cache, TPIDR, PMU, and GIC ICC registers.
- Defines final `SYSREG` macro for C-side numeric encodings.
- Defines barrier domain/type constants like `ISH`, `NSH`, and `SY`.

Dependencies:
- Assembly files temporarily redefine `SYSREG` to Plan 9 assembler `SPR(...)` form.

Research notes:
- This header is shared by C and assembly but intentionally has assembler-specific redefine patterns.
