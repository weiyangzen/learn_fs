# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/optab.c

Instruction selection table for `vl` MIPS code generation.

Key contents:
- Defines `Optab optab[]`, mapping abstract assembler opcodes and operand classes to encoding templates, instruction sizes, and default base registers.
- Covers TEXT, integer moves, arithmetic, shifts, floating point ops, small/large SB/SP/zero-relative memory forms, constants, branches, jumps, HI/LO, floating-control registers, TLB/system ops, CASE, and WORD.
- Uses representative opcodes so `span.c` can clone ranges for equivalent instructions with `buildop()` and `buildrep()`.

Important behavior:
- Table entries encode both size decisions and assembler case numbers later consumed by the output backend.
- Small versus large addressing classes are central to code size and literal decisions.

Risks:
- Comment says several 64-bit and floating double move cases are unfinished.
- Any class/template mismatch reports “illegal combination” during `oplook()`.
