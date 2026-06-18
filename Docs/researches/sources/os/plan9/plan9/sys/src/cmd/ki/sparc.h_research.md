# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/sparc.h

This is the shared header for the `ki` SPARC emulator/debugger. It documents host assumptions for integer and floating-point emulation and includes SPARC `ureg.h`.

It defines breakpoint types, instruction categories, the optional `Icache`, decoded `Inst` entries, the `Registers` structure with integer registers, PC/IR/Y/PSR/FPSR, and a union view over FP registers as doubles, floats, and words.

It defines memory segment structures (`Segment`, `Memory`), segment IDs, syscall memory-copy directions, Plan 9 kernel/user address constants, stack layout constants, NOP encoding, PSR flag bits, immediate extraction helpers, branch annul bit, and FP condition-code values.

The header also declares all emulator subsystems and global state: memory, registers, tracing flags, breakpoint list, Bio streams, current instruction, instruction profile buffer, symbol map, and counters.
