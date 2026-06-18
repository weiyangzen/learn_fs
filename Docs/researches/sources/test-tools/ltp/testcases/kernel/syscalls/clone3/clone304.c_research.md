<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2025 Stephen Bertram <sbertram@redhat.com> \ This test verifies that :manpage:`clone3(2)` fails with EPERM when CAP_SYS_ADMIN has been dropped and ``clone_args.set_tid_size`` is greater than zero. flags = 0 || CLONE_NEW*, set_tid_size > 0 => EPERM flags = CLONE_NEW*, set_tid_size = 0 => EPERM The file was read in full for this report (93 lines, 2132 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`. Important call/API signals are `clone3`, `TST_EXP_FAIL`, `ltp_clone3_raw`, `clone3_supported_by_kernel`, `SAFE_UNSHARE`, `TST_CAP`. Defined constants/macros include `_GNU_SOURCE`, `DESC`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct tst_cap`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLONE_NEW, CLONE_NEWPID, CLONE_NEWCGROUP, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS, CLONE_NEWUSER`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone304.c -->
