# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/reg.c

This is the SPARC backend global register allocator and data-flow optimizer. It builds a flow graph from generated instructions, computes liveness, identifies profitable live ranges, assigns registers, rewrites instructions, then runs peephole optimization.

`regopt()` performs the full pipeline: build `Reg` nodes, record variable use/set bits, resolve branch targets, detect loop structure, propagate liveness backward, propagate register/variable synchronization forward, isolate allocation regions, cost them, assign available integer/FP registers, insert load/store moves, recalculate PCs, patch branches, and remove nops.

Loop analysis uses reverse postorder and approximate dominators following the Hecht-Ullman method. Region costing weights references by loop nesting, penalizes loads/stores, excludes unsafe variables, and handles calls/external variables conservatively.

`mkvar()` maps operands to optimizable variables and classifies externs, params, constants, and address-taken/punned variables. `paint1()`, `paint2()`, and `paint3()` evaluate and apply allocation over live regions. `RtoB`/`BtoR` and `FtoB`/`BtoF` map physical registers to bit masks.

The allocator is performance-critical and assumes exact instruction semantics from `mkvar()` and peephole helpers. It intentionally avoids allocating special registers and respects SPARC integer/FP register classes.
