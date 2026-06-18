<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c

Purpose: 07/2001 John George Verify that: - truncate(2) truncates a file to a specified length successfully. - If the file is larger than the specified length, the extra data is lost. - If the file is shorter than the specified length, the extra data is filled by '0'. - truncate(2) doesn't change offset.

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `tst_test.h`, `tst_safe_prw.h`; exercises `truncate`; defines `verify_truncate`, `setup`, `cleanup`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_truncate`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.cleanup`, `.tcnt`, `.test` into the runner.

State and persistence behavior: Runtime state is regular file content, length, descriptor offsets, permissions, symlink loops, resource limits, and filesystem error paths.

Dependencies and integration points: Depends on temporary filesystem fixtures, `truncate(2)`, resource limits, bad-address helpers, credential switching, and filesystem-specific error behavior. Direct include dependencies include `errno.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `tst_test.h`.

Risks and test signals: Filesystem permissions, RLIMIT_FSIZE, symlink-loop limits, and bad-address checks vary; setup must isolate each errno path. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate02.c -->
