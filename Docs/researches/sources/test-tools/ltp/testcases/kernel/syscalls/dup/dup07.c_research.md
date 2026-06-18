<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE, section2/iosuite/dup3.c, by Airong Zhang Copyright (c) 2013 Cyril Hrubis <chrubis@suse.cz> Copyright (c) Linux Test Project, 2006-2024 \ Verify that the file descriptor created by dup(2) syscall has the same access mode as the old one. The file was read in full for this report (56 lines, 1232 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `SAFE_CREAT`, `TST_EXP_FD_SILENT`, `SAFE_FSTAT`, `tst_res`, `SAFE_CLOSE`, `SAFE_UNLINK`. Relevant structs/types include `struct tcase`, `struct stat`. Harness metadata uses `.test`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup07.c -->
