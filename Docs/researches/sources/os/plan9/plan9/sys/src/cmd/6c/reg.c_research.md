# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/reg.c

This is the amd64 compiler register allocator and global data-flow optimizer. It builds a control-flow graph from emitted `Prog` instructions, identifies variable references, computes branches, detects loops, propagates liveness, selects register-allocation regions, paints variables into registers, inserts loads/stores, runs peephole optimization, recalculates PCs, fixes branches, and removes NOPs.

`mkvar` maps addressable autos, params, statics, and externs into bitset variables, while marking address-taken or punning cases as unsafe. `prop` propagates references and call-live sets backward. `synch` computes register/memory divergence forward. `loopit` uses reverse postorder and approximate dominators to weight loops.

`paint1` scores profitable regions, `paint2` determines unavailable registers, `allreg` chooses integer or XMM registers, and `paint3` rewrites operand addresses to selected registers. `addmove` inserts memory/register synchronization moves.

The allocator reserves architectural registers such as stack, return, argument, and external registers, and handles special instruction register uses.

Filesystem relevance is high at the build level: this determines register quality for all amd64 Plan 9 C code, including filesystem code paths.
