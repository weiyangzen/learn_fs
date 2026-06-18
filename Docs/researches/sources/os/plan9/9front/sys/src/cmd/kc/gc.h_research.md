# File Research: sources/os/plan9/9front/sys/src/cmd/kc/gc.h

Shared SPARC compiler backend header. It defines target sizes, object address and instruction records (`Adr`, `Prog`), switch-case metadata, multiply-constant tables, register allocator variables (`Var`, `Reg`, `Rgn`), global backend state, bitset macros, cost constants, and function prototypes for all backend modules.

The header binds this compiler to `../kc/k.out.h` opcode/address enums and `../cc/cc.h` frontend types. Its declarations describe the backend phases: code generation (`cgen`, `sugen`), instruction emission (`txt.c`), switch/bitfield/data output (`swt.c`), listing formatters, register allocation, peephole optimization, and 64-bit helper code. It is the integration point for this architecture port.
