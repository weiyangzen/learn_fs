<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c

Purpose: Directory-focused file attribute coverage, including flags that affect directory mutation semantics. Source notes: \ Verify that `file_getattr` and `file_setattr` are correctly raising an error when the wrong file descriptors types are passed to them. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (62 lines, 1203 bytes).

Important APIs/types/functions: calls/wrappers: TST_EXP_FAIL, TST_FD_FOREACH, SAFE_TOUCH; types/structs: struct file_attr, struct tst_fd, struct tst_test, struct tst_buffers; functions: test_invalid_fd, run, setup; local macros/constants: FILENAME.

Control flow: setup path: setup; exercise path: test_invalid_fd, run; notable execution mechanics: runs across syscall ABI variants.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fs.h`; integrates with the LTP file_attr syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit failure reporting; errno checks: ENOTDIR; harness metadata: .test_all, .setup, .test_variants, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/file_attr/file_attr04.c -->
