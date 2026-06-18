<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c

Purpose: reproduces the set_mempolicy 32-bit compat syscall information-leak regression by placing a known byte pattern on the user stack, issuing the compat-style syscall with invalid node-mask arguments, and verifying that the stack pattern is not overwritten before the kernel returns EFAULT or EINVAL. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `set_mempolicy`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`.

State and persistence behavior: exercises user-stack contents, compat syscall argument handling, and NUMA policy validation without creating durable files or changing repository state. The test keeps all observable state in the local stack buffer and syscall return code.

Dependencies and integration points: depends on architecture gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy05.c -->
