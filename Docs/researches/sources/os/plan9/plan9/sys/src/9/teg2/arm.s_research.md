# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arm.s

Tegra 2 ARM assembly macro include for early startup, exception return, MMU/cache setup, barriers, and low-level CP15 operations.

Key responsibilities:
- Defines physical/virtual conversion macros, L1 index calculations, CPU0 Mach placement, and initial section PTE constants for DRAM and I/O.
- Provides early serial `PUTC`, delay-loop, zero-segment SB setup, and page-table fill/zero macros.
- Encodes ARMv7 instructions and barriers not directly expressed by older Plan 9 assembler syntax: `SMC`, branch-target-cache flushes, `DSB`, `DMB`, `ISB`, `WFI`, `CLZ`, endian/mode/interrupt CPS instructions, `CLREX`, and VFP control moves.
- Defines `BARRIERS` as branch-target flush plus DSB/ISB for PTE/cache/TLB update sequences.
- Defines ARMv7 `RFE` instruction encodings and CPU ID extraction macro.

Role:
- This is included by low-level assembly, not a standalone routine file.
- It bridges Plan 9 assembler conventions with ARMv7/Cortex-A9 hardware requirements.

Notable constraints:
- Comments warn that Plan 9 assembler `RFE` syntax does not mean the ARMv7 architectural `RFE` instruction.
- Several macros depend on code running before or after MMU enable and therefore adjust addresses to match the current segment.
