# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/power.h

Shared declarations, state, constants, and decode macros for the PowerPC interpreter/debugger.

Key contents:
- Includes PowerPC user register layout from `/power/include/ureg.h`.
- Defines breakpoint, instruction, opcode table, instruction-cache, register-file, segment, and memory structures.
- Declares emulator functions across branch, integer, float, memory, syscall, command, symbol, stats, and loader modules.
- Declares global emulator/debugger state.
- Defines Plan 9 user address, stack, page, profiling, NOP, CR, FPSCR, XER, and opcode decode constants/macros.

Dependencies:
- Consumed by all `qi` C files.
- Depends on Plan 9 libmach types and PowerPC Ureg layout.

Notable risks:
- Header comments document host assumptions for floating emulation: word/double sizes, padding, and `vlong` precision.
- Global state is broad and mutable across all modules.
- Some declared names differ from implementations (`initicache` vs `icacheinit`), reflecting old-code looseness.
