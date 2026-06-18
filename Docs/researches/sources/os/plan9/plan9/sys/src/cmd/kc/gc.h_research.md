# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/gc.h

This is the SPARC C compiler backend master header. It includes the shared C compiler header and SPARC object format header, then defines target sizes, backend IR structures, global state, macros, and function prototypes.

Important structures include `Adr` for instruction operands, `Prog` for generated instructions, `Case`/`C1` for switch lowering, `Multab`/`Hintab` for multiply optimization, `Var` for register-allocation variables, `Reg` for control-flow/data-flow graph nodes, and `Rgn` for allocatable live regions.

Global state covers code lists, string data, rathole temporaries, switch cases, register allocation regions, live-variable bitsets, used registers, flow graph nodes, and target-specific external register offsets.

The prototypes define the backend modules: simple generation, expression generation, text/instruction emission, switch/bitfield/object output, listing, global register allocation, peephole optimization, and 64-bit helper lowering.
