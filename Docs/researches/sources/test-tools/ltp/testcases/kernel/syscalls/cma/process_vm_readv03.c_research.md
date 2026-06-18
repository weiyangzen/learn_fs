<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c

Purpose: LTP regression coverage for `process_vm_readv` behavior. Source intent: Copyright (c) International Business Machines Corp., 2012 Copyright (c) Linux Test Project, 2012 Copyright (C) 2021 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Fork two children, one child mallocs randomly sized trunks of memory and initializes them; the other child calls process_vm_readv with the remote iovecs initialized to the original process memory locations and the local iovecs initialized to. The file was read in full for this report (196 lines, 5259 bytes).

Important APIs/types/functions: Primary functions are `create_data_size`, `child_alloc`, `child_read`, `setup`, `cleanup`, `run`. Important call/API signals are `create_data_size`, `SAFE_MALLOC`, `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `child_read`, `TST_EXP_POSITIVE`, `tst_syscall`, `process_vm_read`, `tst_brk`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_strstatus`, `TST_CHECKPOINT_WAKE`. Defined constants/macros include `MAX_IOVECS`. Relevant structs/types include `struct tcase`, `struct iovec`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`; child-oriented functions `child_alloc, child_read`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, process address-space and iovec buffers. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<sys/types.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `cma` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: remote-memory tests depend on ptrace-style permission checks and child synchronization

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .setup, .cleanup, .tcnt, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/cma/process_vm_readv03.c -->
