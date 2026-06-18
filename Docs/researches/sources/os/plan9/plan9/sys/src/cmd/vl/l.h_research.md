# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/l.h

Purpose: Central declarations for the Plan 9 MIPS linker.

Key behavior:
- Defines linker address, program, symbol, auto, opcode table, opcode range, and count structures.
- Defines symbol classes, operand classes, scheduler flags, sizing constants, and global state.
- Declares output layout parameters, buffers, current program/text state, symbol hash, library lists, op tables, debug flags, and statistics.
- Declares all major linker passes and helpers.

Dependencies:
- Includes Plan 9 headers, MIPS object definitions from `../vc/v.out.h`, and ELF definitions from `../8l/elf.h`.

Notable details:
- Uses the Plan 9 style `EXTERN` pattern so the same header can define or declare globals depending on including source.
