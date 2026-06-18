# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fmt.c

`fmt.c` provides debug formatters for emulator instructions, flags, and CPU state. `%I` formats decoded instructions, `%J` formats selected flags, and `%C` formats a full CPU line with registers, flags, current opcode, and disassembly.

Instruction formatting understands registers, immediates, far pointers, relative targets, ModR/M memory forms, segment overrides, 16/32-bit address expressions, REP prefixes, and conditional jump mnemonic selection. It protects memory dereferences while formatting by saving/restoring the CPU jump buffer.

The code is diagnostic infrastructure used by `realemu/main.c` tracing.
