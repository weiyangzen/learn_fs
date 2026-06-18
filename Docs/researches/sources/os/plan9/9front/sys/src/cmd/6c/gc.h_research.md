# File Research: sources/os/plan9/9front/sys/src/cmd/6c/gc.h

- Role: Central amd64 C compiler backend header for 9front `6c`, shared by code generation, register allocation, peephole optimization, switch lowering, and object emission.
- Defines target sizing constants for amd64 under Plan 9 compiler conventions: 4-byte `long`, 8-byte pointer/vlong/double, 4-byte float.
- Defines compiler backend IR structures: `Adr` for assembly operands, `Prog` for emitted instructions, `Case`/`C1` for switch cases, `Var` for register allocator variables, `Reg` for control-flow graph nodes, `Rgn` for allocation regions, and `Renv` for register environments.
- Declares global compiler state: program list pointers, `pc`, string literal buffering, case list state, register-use arrays, live-variable bitsets, and register allocator worklists.
- Provides liveness macros `BLOAD`, `BSTORE`, `LOAD`, and `STORE`, plus cost constants for allocation heuristics.
- Exposes prototypes for 6c modules: expression/code generation, 64-bit helpers, text/object output, switch/data output, listing formatters, register allocation, peephole optimization, target-bound helpers, and multiply/divide helpers.
- Important integration point: this header binds 6c to shared front-end headers `../cc/cc.h` and amd64 opcode/address definitions in `../6c/6.out.h`.
