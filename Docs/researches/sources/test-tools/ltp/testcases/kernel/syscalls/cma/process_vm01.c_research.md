<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c

Purpose: LTP regression coverage for `process_vm_readv/process_vm_writev` behavior. Source intent: Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Test errno codes in process_vm_readv and process_vm_writev syscalls. only flags == 0 is allowed, everything else should fail with EINVAL collect result from child before the next test, otherwise TFAIL/TPASS messages will arrive asynchronously The file was read in full for this report (312 lines, 7011 bytes).

Important APIs/types/functions: Primary functions are `free_params`, `test_readv`, `test_writev`, `check_errno`, `test_sane_params`, `test_flags`, `test_iov_len_overflow`, `test_iov_invalid`, `test_invalid_pid`, `test_invalid_perm`, `test_invalid_protection`, `run`, `setup`. Important call/API signals are `SAFE_MALLOC`, `test_readv`, `TEST`, `tst_syscall`, `test_writev`, `tst_res`, `TST_EXP_EQ_LI`, `tst_get_unused_pid`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETUID`, `tst_reap_children`, `SAFE_MMAP`, `SAFE_MUNMAP`. Relevant structs/types include `struct process_vm_params`, `struct iovec`, `struct passwd`, `struct tst_option`. Harness metadata uses `.test_all`, `.setup`, `.needs_root`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `test_readv, test_writev, test_sane_params, test_flags, test_iov_len_overflow, test_iov_invalid`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, process address-space and iovec buffers, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<pwd.h>`, `<stdlib.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EFAULT, ESRCH, EPERM`; harness fields `.test_all, .setup, .needs_root, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm01.c -->
