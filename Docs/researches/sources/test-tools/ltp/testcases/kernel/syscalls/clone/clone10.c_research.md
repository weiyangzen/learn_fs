<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) 2025 Red Hat Inc. Author: Chunfu Wen <chwen@redhat.com> \ Test that in a thread started by clone() that runs in the same address space (CLONE_VM) but with a different TLS (CLONE_SETTLS) writtes to a thread local variables are not propagated back from the cloned thread. The file was read in full for this report (99 lines, 2080 bytes).

Important APIs/types/functions: Primary functions are `touch_tls_in_child`, `verify_tls`, `setup`, `cleanup`. Important call/API signals are `clone`, `tst_atomic_store`, `tst_syscall`, `TEST`, `ltp_clone7`, `tst_brk`, `tst_atomic_load`, `tst_res`, `syscall`, `SAFE_MALLOC`. Defined constants/macros include `_GNU_SOURCE`, `TLS_EXP`, `ARCH_SET_FS`. Relevant structs/types include `struct user_desc`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_tls`; cleanup-oriented functions `cleanup`; child-oriented functions `touch_tls_in_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<stdio.h>`, `<errno.h>`, `<sched.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"clone_platform.h"`, `"lapi/syscalls.h"`, `"tst_atomic.h"`, `"lapi/tls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_VM, CLONE_SETTLS, CLONE_THREAD, CLONE_FS, CLONE_FILES, CLONE_SIGHAND`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone10.c -->
