# File Research: sources/os/plan9/9front/sys/src/cmd/2c/gc.h

Purpose: central 68020 compiler-backend header for `2c`.

Key contents:
- Includes common C front-end state `../cc/cc.h` and target object ABI `../2c/2.out.h`.
- Defines target sizes for char/short/int/long/pointer/float/vlong/double and backend constants such as `FNX`, `INDEXED`, and side-effect flags.
- Declares backend structures: `Adr`, `Prog`, `Txt`, `Cases`, `Var`, `Reg`, `Rgn`, `Multab`, `C1`, and `Index`.
- Declares global compiler backend state for instruction list, switch cases, register allocation, variables, static/string/rathole areas, loop/dataflow arrays, register usage masks, and opcode conversion tables.
- Defines dataflow cost constants and macros for load/store/ref/call bit operations.
- Prototypes all target backend functions across expression codegen, listing, peephole, register allocation, statement generation, switch/object output, and text emission.
- Registers Plan 9 `Fmt` format specifiers for target-specific printing.

Research notes:
- `Adr` here matches object/linker address semantics but carries compiler-only `etype`.
- `Reg` is both CFG node and dataflow record for global register allocation.
- `Txt txt[NTYPE][NTYPE]` and `opxt[ALLOP][NTYPE]` are initialized in `txt.c` and drive type-dependent instruction choice.
