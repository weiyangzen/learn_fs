<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> \ Basic clone3() test. The file was read in full for this report (188 lines, 3825 bytes).

Important APIs/types/functions: Primary functions are `parent_rx_signal`, `child_rx_signal`, `do_child`, `run`, `setup`. Important call/API signals are `clone3`, `SAFE_SIGACTION`, `TST_CHECKPOINT_WAKE`, `tst_res`, `tst_strsig`, `TEST`, `ltp_clone3_raw`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `clone3_supported_by_kernel`. Defined constants/macros include `_GNU_SOURCE`, `CHILD_SIGNAL`, `DATA`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct sigaction`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_checkpoints`, `.needs_kconfigs`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child_rx_signal, do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/sched.h"`, `"lapi/pidfd.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_FS, CLONE_NEWPID, CLONE_PARENT_SETTID, CLONE_CHILD_SETTID, CLONE_PIDFD`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_checkpoints, .needs_kconfigs`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone301.c -->
