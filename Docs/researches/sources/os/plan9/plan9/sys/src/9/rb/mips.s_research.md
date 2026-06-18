# File Research: sources/os/plan9/plan9/sys/src/9/rb/mips.s

MIPS 24K assembly macro include for the RouterBoard port. It defines instruction encodings and helper macros used by startup, exception, cache, TLB, and reboot assembly.

Key responsibilities:
- Defines symbolic register aliases (`SP`, `MACH`, `USER`) and basic instruction macros such as `NOP`, `CONST`, and `RETURN`.
- Encodes MIPS32R2 operations not directly named by the assembler: `DI`, `EI`, `EHB`, `JALRHB`, `JRHB`, `MFC0`, `MTC0`, `RDHWR`, `SYNC`, and `WAIT`.
- Wraps `ERET` with hazard barriers and a post-ERET NOP for MIPS 24K behavior.
- Provides barrier macros that jump through a hazard-barrier return sequence, including a KSEG1 variant.
- Provides a direct serial `PUTC` macro using `PHYSCONS`.
- Defines cache operation encodings for primary data/instruction and secondary/tertiary cache operations.

Role:
- This file is not a standalone implementation; it is an assembly support header included by other MIPS assembly files.
- It centralizes CPU-specific erratum/hazard handling so trap and MMU assembly can use consistent barriers.

Notable constraints:
- Several operations are raw `WORD` encodings, so correctness depends on MIPS32R2 instruction layout and the Plan 9 assembler's expectations.
- The comments explicitly tie some sequences to MIPS 24K errata and experience with required hazard barriers.
