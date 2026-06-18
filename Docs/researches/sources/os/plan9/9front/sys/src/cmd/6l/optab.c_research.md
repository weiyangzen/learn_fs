# File Research: sources/os/plan9/9front/sys/src/cmd/6l/optab.c

- Role: amd64/x86 instruction encoding table for 6l.
- Defines operand pattern arrays (`y*`) mapping accepted from/to operand classes to encoding templates and opcode widths.
- `optab[]` maps Plan 9 assembly opcodes to operand patterns, prefix rules, and raw opcode bytes.
- Covers integer arithmetic/logical ops, shifts/rotates, moves and extensions, branches/calls/returns, stack ops, string ops, segment/control/debug/task register moves, x87 FPU, MMX, SSE/SSE2/SSE3-style media operations, system instructions, fences, syscall/sysret, cmpxchg/xadd, and pseudo/data ops.
- Prefix codes express operand-size override, 0x0f opcode escape, REX.W, byte mode, SSE prefixes F2/F3, 32-bit-only, and 64-bit-only constraints.
- `opindex[]` is the runtime opcode-to-table index populated in `obj.c`.
- This file is data-centric: behavioral correctness depends on `span.c` interpreting `Y*`, `Z*`, and `P*` consistently.
