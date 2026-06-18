# File Research: sources/os/plan9/9front/sys/src/cmd/2c/reg.c

Purpose: global register allocator and dataflow optimizer for the 68020 compiler backend.

Key behavior:
- `regopt()` builds a CFG from emitted `Prog` instructions, skipping pseudo-ops, assigning PCs, use/set bitsets, branch edges, and logarithmic search links.
- Converts branch offsets to `Reg` edges and computes loop structure using reverse postorder and approximate dominators from the Hecht-Ullman dataflow method.
- Propagates liveness and call-clobber information backward with `prop()`, then register/variable synchrony forward with `synch()`.
- Finds candidate live regions, computes benefit costs with `paint1()`, determines blocked registers with `paint2()`, chooses data/address/FPU registers with `allreg()`, and rewrites operands plus loads/stores with `paint3()`.
- Warns on used-before-set and set-but-unused variables; can excise unused stores.
- `mkvar()` maps addressable autos, params, statics, and externs to optimizer variable bits while excluding unsafe/punned/address-taken values.
- Final pass recalculates PCs, fixes branch offsets, removes `ANOP`s, and returns `Reg` nodes to a freelist.

Research notes:
- Integer/pointer values may choose either data or address registers depending on cost; floats choose FPU registers.
- Calls mark externs and live refs as clobbered; returns and text boundaries reset flow assumptions.
- `addmove()` preserves CCR around inserted moves when needed.
