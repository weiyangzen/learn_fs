# File Research: sources/os/plan9/9front/sys/src/cmd/tc/gc.h

Defines shared data structures, constants, globals, and prototypes for the Thumb C compiler backend.

Key points:
- Includes common C compiler definitions and ARM object definitions from `../cc/cc.h` and `../5c/5.out.h`.
- Sets target type sizes for Thumb: 1-byte char, 2-byte short, 4-byte int/long/pointer/float, 8-byte vlong/double.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global codegen, register allocation, control-flow, switch, string, and optimization state.
- Defines register allocator bitset helpers and cost constants.
- Declares function prototypes for `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, and `peep.c`.
- Registers custom Plan 9 `Fmt` conversions for instructions, addresses, registers, symbols, and bitsets.

Dependencies and interactions:
- Every `tc` backend source includes this file.
- Shared with assembler/object constants from the ARM toolchain headers.

Research relevance:
- This is the interface contract tying together the backend files in this group.
