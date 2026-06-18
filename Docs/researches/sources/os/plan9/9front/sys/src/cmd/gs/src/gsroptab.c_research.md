# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsroptab.c

Provides the concrete table of 256 RasterOp procedures plus the operand-usage table.

Key behavior:
- Defines one `ropN(D,S,T)` function for each 8-bit ROP3 opcode, using expressions derived from HP/Microsoft reverse Polish notation names.
- Exports `rop_proc_table[256]`, mapping opcode values directly to implementation functions.
- Exports `rop_usage_table[256]`, whose entries encode whether each operation uses D, S, T, or combinations of them.
- Includes the small generator program, in a comment, that produced the usage table from `rop3_uses_D/S/T`.

Dependencies:
- Includes only `stdpre.h` and `gsropt.h`; this is a pure Boolean helper table.

Research notes:
- This file is data-heavy but mechanically straightforward: correctness depends on the per-op expressions and direct opcode-to-index table alignment.
