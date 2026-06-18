<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2025 Stephen Bertram <sbertram@redhat.com> \ This test verifies that :manpage:`clone(2)` fails with EPERM when CAP_SYS_ADMIN has been dropped. The file was read in full for this report (81 lines, 1560 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `run`, `setup`, `cleanup`. Important call/API signals are `clone`, `TST_EXP_FAIL`, `ltp_clone`, `SAFE_MMAP`, `SAFE_MUNMAP`, `TST_CAP`. Defined constants/macros include `_GNU_SOURCE`, `DESC`. Relevant structs/types include `struct tcase`, `struct tst_cap`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"clone_platform.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLONE_NEWPID, CLONE_NEWCGROUP, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone11.c -->
