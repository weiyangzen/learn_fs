<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c

Purpose: Verifies parent/child memory or variable state separation after fork. Source notes: \ This test verifies that parent process shares environ variables with the child and that child doesn't change parent's environ variables. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (94 lines, 2015 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_EXPR, TST_CHECKPOINT_WAKE_AND_WAIT, SAFE_SETENV, TST_CHECKPOINT_WAKE, SAFE_FORK, TST_CHECKPOINT_WAIT; types/structs: struct tst_test; functions: run_child, run; local macros/constants: ENV_KEY, ENV_VAL0, ENV_VAL1.

Control flow: exercise path: run_child, run; notable execution mechanics: forks child processes for concurrency or privilege separation, uses LTP checkpoints to order parent/child actions.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; errno checks: ENV_KEY, ENV_VAL0, ENV_VAL1; harness metadata: .test_all, .forks_child, .needs_checkpoints.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork04.c -->
