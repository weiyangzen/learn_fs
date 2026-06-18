# File Research: sources/os/plan9/9front/sys/src/cmd/8l/optab.c

Operand-pattern and opcode encoding table for the 386 linker/assembler backend.

Key contents:
- Defines many `uchar` operand pattern tables mapping source/destination classes to encoding recipes, including integer, branch, stack, x87, MMX, SSE/XMM, segment/control-register, and pseudo-op forms.
- `optab[]` maps every 386 opcode enum to an operand table, required instruction prefix, and concrete opcode bytes or ModRM extension bits.
- Covers core 386 operations, condition branches/sets, string instructions, privileged/control instructions, x87 floating point, MMX/SSE packed operations, and Plan 9 pseudo-ops such as `TEXT`, `DATA`, `GLOBL`, `WORD`, `LONG`, `BYTE`, `END`.
- Ends with `opindex[ALAST+1]`, populated by `obj.c` for fast opcode lookup.

Filesystem relevance: indirect. It is architecture encoding metadata for building Plan 9 binaries.
