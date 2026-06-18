<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-branch.c -->
# sources/test-tools/stress-ng/stress-branch.c

Purpose: `stress-branch.c` implements the `branch` stressor. It uses GCC labels-as-values and a large computed-goto table to produce hard-to-predict indirect branches.

Important APIs/types/functions: the implementation is gated on `HAVE_LABEL_AS_VALUE` and excludes PCC. `RESEED_JMP(n)` updates periodic counters, advances a linear congruential pseudo-random seed, selects the next label, and jumps to the previously selected label. `J(n)` expands each numbered label body. `stress_branch()` contains a 1024-entry static label table and 16 counters, one for every 64th label.

Control flow: after zeroing counters and passing the sync barrier, execution enters label `L0x000`. Each label reseeds and computed-gotos to the next selected label; `L0x000` also increments bogo operations, optionally yields on SH4, and checks `stress_continue(args)`. After stopping, the stressor validates that every sampled 64th label execution count falls within +/-10 percent of the bogo count when enough samples were collected.

State and persistence behavior: state is purely in-process: the seed, next-label pointer, bogo counter, and static counters array. There is no persistent storage or kernel state.

Dependencies and integration points: depends on compiler support for addressable labels, stress-ng process-state handling, bogo counters, architecture macros, and optional scheduler yield. It registers `CLASS_CPU` with `VERIFY_ALWAYS`; unsupported compilers get an unimplemented reason.

Risks: this source is tightly coupled to compiler extensions and optimizer behavior. The distribution check assumes the pseudo-random sequence and sampled labels stay proportional to bogo increments; changes to where bogo is incremented can cause false verification failures. Computed goto can be difficult for sanitizers, coverage tools, and non-GNU compilers.

Test signals: build with GCC/clang, verify unsupported fallback on compilers without labels-as-values, run enough operations to trigger the 10 percent distribution check, and cover SH4/QEMU yield behavior if relevant. Failure messages name the branch label index and expected counter range.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-branch.c -->
