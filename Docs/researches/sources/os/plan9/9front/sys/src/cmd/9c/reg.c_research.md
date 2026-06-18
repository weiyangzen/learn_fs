# File Research: sources/os/plan9/9front/sys/src/cmd/9c/reg.c

Global register optimizer for the PowerPC64 compiler backend.

Key phases in `regopt`:
- Builds `Reg` CFG nodes from emitted instructions while skipping data/name pseudo-ops and assigning synthetic PCs.
- Computes use/set bitsets for variables with `mkvar`, tracks externs, params, constants, address-taken/punned variables, and register usage.
- Resolves branch destinations into CFG successor/predecessor links using skip links.
- Computes loop weights via reverse postorder, approximate dominators, loop-head detection, and loop marking.
- Propagates variable references and call-live information backward with `prop`.
- Propagates register/variable divergence forward with `synch`.
- Identifies profitable allocation regions with `paint1`, computes occupied register masks with `paint2`, selects hardware registers via `allreg`, and rewrites code with `paint3`.
- Inserts load/store moves around allocated regions with `addmove`.
- Runs peephole optimization, recalculates PCs, fixes branch targets, removes NOPs, and recycles `Reg` nodes.
- `RtoB`/`BtoR` and `FtoB`/`BtoF` map allocatable GPR/FPR ranges into optimizer bit masks.

Important constraints:
- Avoids optimizing variables with unsafe punning/address identity or excess variable-table pressure.
- Distinguishes integer and floating register classes and avoids impossible GPR/FPR move patterns.

Filesystem relevance: indirect compiler optimizer.
