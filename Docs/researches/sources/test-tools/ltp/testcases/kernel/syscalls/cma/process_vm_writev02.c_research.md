<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c

Purpose: LTP regression coverage for `process_vm_writev` behavior. Source intent: Copyright (c) International Business Machines Corp., 2012 Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Fork two children, the first one allocates a chunk of memory and the other one call process_vm_writev to write known data into the first child. The file was read in full for this report (127 lines, 2799 bytes).

Important APIs/types/functions: Primary functions are `child_alloc_and_verify`, `child_write`, `setup`, `cleanup`, `run`. Important call/API signals are `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `child_write`, `TST_EXP_POSITIVE`, `tst_syscall`, `tst_brk`, `tst_parse_int`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_strstatus`, `TST_CHECKPOINT_WAKE`. Relevant structs/types include `struct iovec`, `struct tst_option`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `child_alloc_and_verify`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_alloc_and_verify, child_write`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, process address-space and iovec buffers. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<sys/uio.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_writev02.c -->
