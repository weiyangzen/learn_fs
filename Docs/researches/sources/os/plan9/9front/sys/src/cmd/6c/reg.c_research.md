# File Research: sources/os/plan9/9front/sys/src/cmd/6c/reg.c

- Role: Global-ish register optimizer and liveness engine for 6c amd64.
- `regopt()` builds a `Reg` flow graph from emitted `Prog` instructions, assigns pseudo PCs, records predecessor/successor edges, and computes variable use/set bits via `mkvar()`.
- Tracks special implicit register uses for x86 instructions such as multiply/divide using AX/DX, string ops using SI/DI/CX, and I/O ops using DX.
- Performs branch target resolution, loop weighting, backward liveness propagation (`prop()`), forward register/variable synchrony propagation (`synch()`), region discovery, allocation cost calculation, register selection, code rewriting, peephole cleanup, PC recomputation, branch fixup, and NOP removal.
- Loop discovery uses reverse postorder plus approximate dominators based on the Hecht/Ullman data-flow algorithm, implemented by `postorder()`, `rpolca()`, `doms()`, `loophead()`, `loopmark()`, and `loopit()`.
- Region allocation is split into `paint1()` for cost, `paint2()` for forbidden register collection, `allreg()` for choosing an integer or XMM register, and `paint3()` for replacing memory references with register references plus inserted loads/stores.
- `mkvar()` records optimizable extern/static/param/auto variables while excluding unsafe address-taken, type-punned, or unsupported type cases.
- Register bit helpers map Plan 9 register enum values to allocator bitmasks: `RtoB()`, `BtoR()`, `FtoB()`, `BtoF()`.
