<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c

Purpose: Check the basic functionality of the symlink() system call.

Important APIs/types/functions: includes `tst_test.h`; exercises `symlink`; defines `verify_symlink`, `setup`.

Control flow centers on `verify_symlink`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.test_all` into the runner.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TFAIL`, `TST_EXP_POSITIVE`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink02.c -->
