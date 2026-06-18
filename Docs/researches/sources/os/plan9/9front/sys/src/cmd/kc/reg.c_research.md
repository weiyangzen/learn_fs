# File Research: sources/os/plan9/9front/sys/src/cmd/kc/reg.c

Global register allocator and liveness optimizer for SPARC compiler output. `regopt` builds a control-flow graph from `Prog` instructions, maps branch targets, detects loops, propagates live references/call-saved requirements, identifies profitable live ranges, assigns available integer or floating registers, rewrites memory operands into registers, runs peephole optimization, recalculates PCs, fixes branches, and removes nops.

The allocator tracks variables through `mkvar`, liveness through `prop`, register/value divergence through `synch`, and candidate regions through `paint1`/`paint2`/`paint3`. Loop weights raise region cost. `RtoB`/`BtoR` and `FtoB`/`BtoF` encode allocatable register sets. This is the backend’s main optimization pass.
