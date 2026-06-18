# File Research: sources/os/plan9/9front/sys/src/cmd/9a/a.y

Yacc grammar for the PowerPC64 assembler `9a`.

Key behavior:
- Parses labels, variable assignments, `SCHED`/`NOSCHED`, and assembler instructions.
- Covers integer/byte loads and stores, floating loads/stores, FPSCR moves, condition-register moves, special-register moves, arithmetic/logical/shift operations, multiply-accumulate, branches/traps, floating operations, comparisons, rotate/mask operations, indexed load/store/move/op forms, no-ops, `WORD`/`DWORD`, `TEXT`, `GLOBL`, `DATA`, `RETURN`, and `END`.
- Builds `Gen` operands for registers, floating registers, condition registers, special registers, FPSCR fields, immediates, string/floating constants, names, static symbols, branch targets, register-indirect and indexed addressing.
- Branch grammar supports direct labels, PC-relative constants, branch-to-address, branch-to-LR/CTR-like special registers, condition fields, and BO/BI-style condition operands.
- `mask` rule turns PowerPC rotate-mask start/end pairs into a bitmask constant.
- Expression grammar handles unary signs/complement and arithmetic/bitwise operators.

Filesystem relevance: indirect assembler frontend for the PowerPC64 toolchain.
