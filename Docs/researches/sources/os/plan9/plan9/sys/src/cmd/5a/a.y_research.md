# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/a.y

Yacc grammar for Plan 9 ARM assembly syntax.

Key behavior:
- Parses labels, variable definitions, directives, instructions, conditions, operands, register lists, shifts, constants, names, and expressions.
- Emits object records through `outcode`.
- Supports ARM data-processing, moves, branches, SWI, comparisons, MOVM, swaps, RET/RFE, TEXT/GLOBL/DATA/WORD/END, floating-point ops, MRC/MCR, multiply-long, and multiply-accumulate forms.
- Encodes `MRC/MCR` directly into `AWORD` using constructed ARM instruction bits.
- Handles conditional suffixes and addressing-mode suffix bits.

Notes:
- Branch labels resolve differently in pass 1 versus pass 2.
- Register list syntax expands to bitmasks used by `MOVM`.
